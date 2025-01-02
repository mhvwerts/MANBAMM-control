/*******************************************************************************
 * Firmware for MOLTECH-Flashbox
 *
 * Generate TTL pulse trains of adjustable width, phase and period.
 * Adjustment takes plase via USB/serial RS232-style interface.
 *
 * The MOLTECH-Flashbox has been designed for use with the digital phosphoroscope
 * set-up
 *
 * This code targets the Arduino Duemilanove board with ATMega168 controller
 * (recycle and reuse of old electronics!) but works without modification 
 * on any modern Arduino UNO with ATMega328p controller
 *
 * M. H. V. Werts, 2024
 * MOLTECH-Anjou, CNRS, Université d'Angers
 * France
 ******************************************************************************/

/* Changelog

mw241201  Set baudrate to 19200; 115200 is deemed unreliable. One should actually
          use baudrates that fit best with 16 MHz. 115200 is not one of them.
          I think that this was already tested by us in the past. It is possible
          to go up to 500000 (500 kbps) with very reliable comms, simply stick
          to only those baudrates that fit with 16 MHz. 115200 is a multiple
          of the historic 9600 baud value, which was not conceived with 16 MHz
          in mind.

*/

/* Some test results. Measuring the TTL pulses with an oscilloscope.

v241130-13h29 (firmwave v1.0)

Period
Value	                Period time (s)
350000	              2.187
320000	              2.000

100                 625.8 us (measured)


Pulse width
Delta value (ON-OFF)	Pulse width (ms)
32000	                200.0
76000	                475.0
78000	                487.5
80000	                500.0

1						  7.691 us




rise time 7 ns (no load) SCOPE LIMITED
fall time 7 ns (no load) SCOPE LIMITED

*/

// Hardware and firmware info - TODO: let device output these if requested
const char *DEV_ID = "MOLTECH Flashbox 01"; // each device should have a unique identifier
const char *FIRMWARE_VERSION = "1.0";


#include <avr/io.h>
#include <stdint.h>
#include <stdbool.h>

// for USART_ReceiveDecimal
#define MAX_DIGITS 10  // Max digits for a 32-bit signed integer

// for state machine
#define MAXSTATE 2
#define FLASHING 0
#define WAITING 1
#define ERROR 2
const char statechr[MAXSTATE+1] = "!.E";

volatile unsigned char state;

// for counter register
// these initial values give the shortest pulse (7.691us) with a 625.8 us period
uint32_t cnt_on = 0UL;
uint32_t cnt_off = 1UL; // delta = 1
uint32_t cnt_period = 100UL;

// // these initial values give a 2s period with a 0.5s flash
// uint32_t cnt_on = 1000UL;
// uint32_t cnt_off = 81000UL; // delta = 80000
// uint32_t cnt_period = 320000UL;

volatile uint32_t cnt;



/* USART routines */

void USART_Init(void) {
  uint16_t ubrr_value = 51; // Baud rate 19200, 16 MHz clock
  UBRR0H = (uint8_t)(ubrr_value >> 8);
  UBRR0L = (uint8_t)(ubrr_value);
  UCSR0B = (1 << RXEN0) | (1 << TXEN0); // Enable RX and TX
  UCSR0C = (1 << UCSZ01) | (1 << UCSZ00); // 8 data bits, 1 stop bit, no parity
}

void USART_Transmit(char data) {
  while (!(UCSR0A & (1 << UDRE0))); // Wait for empty transmit buffer
  UDR0 = data;
}

char USART_Receive(void) {
  while (!(UCSR0A & (1 << RXC0))); // Wait for data to be received
  return UDR0;
}


int32_t USART_ReceiveDecimal(void) {
  int32_t result = 0;
  uint8_t digit_count = 0;
  char received_char;

  while (1) {
    // Wait for a character
    while (!(UCSR0A & (1 << RXC0)))
      ;
    received_char = UDR0;  // Read the character

    // Check if the character is a valid digit
    if (received_char >= '0' && received_char <= '9') {
      // Decode the digit and add it to the result
      if (digit_count >= MAX_DIGITS) {
        return -1; // Too many digits (integer overflow risk)
      }

      result = result * 10 + (received_char - '0');
      digit_count++;
    } 
    // Check for the termination character 'd'
    else if (received_char == 'd') {
      return result; // Successfully decoded number
    } 
    // Invalid character
    else {
      return -1; // Error: Invalid character in input
    }
  }
}





/* main() loop */

int main(void) {
  char in_char; 
  int32_t setvalue;

  // Configure PB3 (Arduino Pin 11) as output
  DDRB |= (1 << PB3);

  // Set Pin 11 LOW
  PORTB &= ~(1 << PB3);

  // Initialize USART
  USART_Init();

  // reset counter register (32 bit unsigned)
  cnt = 0;

  state = FLASHING;

  while(state <= MAXSTATE) {
    if (state == FLASHING) {
      if (cnt == cnt_on) {
        // Set Pin 11 HIGH
        PORTB |= (1 << PB3);
      }
      if (cnt == cnt_off) {
        // Set Pin 11 LOW
        PORTB &= ~(1 << PB3);
      }
      cnt++;
      if (cnt == cnt_period) {
        // Set Pin 11 LOW (not really necessary)
        PORTB &= ~(1 << PB3);
        cnt = 0;
      }
    }

    // Poll for incoming data and change state or act
    if (UCSR0A & (1 << RXC0)) {
      in_char = UDR0; // Read the received character
      switch (in_char) {
        case '!':   // Set state to flashing (pulse outpu)
          state = FLASHING;
          break;

        case '.':   // Set state to waiting (no pulse output)
          state = WAITING;
          break;

        case '?':  // Output current state
          USART_Transmit(statechr[state]);
          break;

        case 'P':   // Set period
          setvalue = USART_ReceiveDecimal();
          if (setvalue > 0) {
            cnt_period = (uint32_t) setvalue;
            cnt = 0; // do not forget to reset counter when changing values!
          }
          else {
            state = ERROR;
          }
          break;

        case 'N':   // Set ON time
          setvalue = USART_ReceiveDecimal();
          if (setvalue >= 0) {
            cnt_on = (uint32_t) setvalue;
            cnt = 0; // do not forget to reset counter when changing values!
          }
          else {
            state = ERROR;
          }
          break;

        case 'F':   // Set OFF time
          setvalue = USART_ReceiveDecimal();
          if (setvalue >= 0) {
            cnt_off = (uint32_t) setvalue;
            cnt = 0; // do not forget to reset counter when changing values!
          }
          else {
            state = ERROR;
          }
          break;

        default:  // Unknown command
          state = ERROR; // Set error indication
          break;
      }
    }
  }

  return 0;
}  