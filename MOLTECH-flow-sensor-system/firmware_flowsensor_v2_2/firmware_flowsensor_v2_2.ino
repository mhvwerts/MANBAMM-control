/*******************************************************************************
 * Purpose: Basic communication between Sensirion liquid flow sensor 
 *          and a computer terminal via a serial RS232-style interface
 *
 *          Based on Example code for the I2C communication with Sensirion
 *          Liquid Flow Sensors
 *
 *          Reads the scale factor and measurement unit information from the
 *          sensor's EEPROM
 *
 *          Reads the raw measurement data from the sensor and transmits it to
 *          the serial interface
 *
 *          This code was initially developed with the Seeeduino XIAO board, but
 *          should also work easily with a standard Arduino UNO board.
 *
 *          This firmware works with the Raspberry Pi Pico 1 board using the
 *          Arduino-Pico environment. No modifications to the code are needed.
 *          Pin connections (no additional resistors needed):
 *            SDA (brown wire) to Pico pin 6 (I2C0 SDA)
 *            SCL (red wire) to Pico pin 7 (I2C0 SCL)
 *            GND (yellow wire) to Pico pin 8 (GND)
 *            V_DD (orange wire) to Pico pin 40 (VBUS)
 *            (green wire is not connected, left floating as per datasheet)
 *
 *          M. Loumaigne and M. H. V. Werts, 2024
 *          MOLTECH-Anjou, CNRS, Université d'Angers
 *          France
 ******************************************************************************/

/* Changelog
    mw241207  Success with Raspberry Pi Pico (RP2040) and Arduino-Pico

    mw241119  Further clean-up. Added 'R' raw measurement output.
              Change termination character to '!'. Serial timeout 1000ms.

    mw241112  Adapted the original code by Loumaigne
              - removed the OLED display interface, which did not work anyway
              - changed the printing and input routines
*/


/*******************************************************************************
 * Specific compile-time configuration for each individual sensor device
 ******************************************************************************/
const char *DEV_ID = "MOLTECH flow sensor 04"; // each device should have a unique number
const char *FIRMWARE_VERSION = "2.2";
const int ADDRESS = 0x40; // Standard address for Liquid Flow Sensors

#include <Wire.h>

// Further configuration
const bool VERBOSE_OUTPUT = true; // set to false for less verbose output

// EEPROM Addresses for factor and unit of calibration fields 0,1,2,3,4.
const uint16_t SCALE_FACTOR_ADDRESSES[] = {0x2B6, 0x5B6, 0x8B6, 0xBB6, 0xEB6};
const uint16_t UNIT_ADDRESSES[] =         {0x2B7, 0x5B7, 0x8B7, 0xBB7, 0xEB6};

// Flow Units and their respective codes.
const char    *FLOW_UNIT[] = {"nl/min", "ul/min", "ml/min", "ul/sec", "ml/h"};
const uint16_t FLOW_UNIT_CODES[] = {2115, 2116, 2117, 2100, 2133};

uint16_t scale_factor;
const char *unit;

int delay_measurement_ms = 1000;

// serial communications buffer
#define BUFFER_ENTREE_LEN 10
unsigned short nb_char;
unsigned short max_char = BUFFER_ENTREE_LEN - 2;
char buffer_entree[BUFFER_ENTREE_LEN];


/******************************************************************************
	Routines
 ******************************************************************************/

// -----------------------------------------------------------------------------
// Sensor communication routines
// -----------------------------------------------------------------------------

void get_sensor_info()
{
  int ret;

  uint16_t user_reg;
  uint16_t scale_factor_address;

  uint16_t unit_code;

  byte crc1;
  byte crc2;

  Serial.println();
  do {
    delay(1000); // Error handling for example: wait a second, then try again

    // Soft reset the sensor
    Wire.beginTransmission(ADDRESS);
    Wire.write(0xFE);
    ret = Wire.endTransmission();
    if (ret != 0) {
      Serial.print("Error while sending soft reset command, retrying...!");
      continue;
    }
    delay(50); // wait long enough for reset

    // Read the user register to get the active configuration field
    Wire.beginTransmission(ADDRESS);
    Wire.write(0xE3);
    ret = Wire.endTransmission();
    if (ret != 0) {
      Serial.print("Error while setting register read mode!");
      continue;
    }

    Wire.requestFrom(ADDRESS, 2);
    if (Wire.available() < 2) {
      Serial.print("Error while reading register settings!");
      continue;
    }


    user_reg  = Wire.read() << 8;
    user_reg |= Wire.read();

    // The active configuration field is determined by bit <6:4>
    // of the User Register
    scale_factor_address = SCALE_FACTOR_ADDRESSES[((user_reg & 0x0070) >> 4)];
    // Serial.print("scale_factor_address : "); 
    // Serial.println(scale_factor_address);
    // Read scale factor and measurement unit
    Wire.beginTransmission(ADDRESS);
    Wire.write(0xFA); // Set EEPROM read mode
    // Write left aligned 12 bit EEPROM address
    Wire.write(scale_factor_address >> 4);
    Wire.write((scale_factor_address << 12) >> 8);
    ret = Wire.endTransmission();
    if (ret != 0) {
      Serial.print("Error during write EEPROM address!");
      continue;
    }

    // Read the scale factor and the adjacent unit
    Wire.requestFrom(ADDRESS, 6);
    if (Wire.available() < 6) {
      Serial.print("Error while reading EEPROM!");
      continue;
    }
    scale_factor = Wire.read() << 8;
    scale_factor|= Wire.read();
    crc1         = Wire.read();
    unit_code    = Wire.read() << 8;
    unit_code   |= Wire.read();
    crc2         = Wire.read();

    switch (unit_code) {
     case 2115:
       { unit = FLOW_UNIT[0]; }
       break;
     case 2116:
       { unit = FLOW_UNIT[1]; }
       break;
     case 2117:
       { unit = FLOW_UNIT[2]; }
       break;
     case 2100:
       { unit = FLOW_UNIT[3]; }
       break;
     case 2133:
       { unit = FLOW_UNIT[4]; }
       break;
     default:
       Serial.print("Error: No matching unit code!");
       break;
   }

    if (VERBOSE_OUTPUT) {
      Serial.println("-------------------------");
      Serial.print("Scale factor: ");
      Serial.println(scale_factor);
      Serial.print("Units: ");
      Serial.println(unit);
      Serial.print("Units code: ");
      Serial.println(unit_code);
      Serial.print("Firmware version: ");
      Serial.println(FIRMWARE_VERSION);
      Serial.println("-------------------------");
      Serial.print("!");
    }

    // Switch to measurement mode
    Wire.beginTransmission(ADDRESS);
    Wire.write(0xF1);
    ret = Wire.endTransmission();
    if (ret != 0) {
      Serial.print("Error during write measurement mode command!");
    }
  } while (ret != 0);

}


void do_measurement(bool raw_output)
{
  int ret;
  uint16_t raw_sensor_value;
  float sensor_reading;

  Wire.requestFrom(ADDRESS, 2); // reading 2 bytes ignores the CRC byte
  if (Wire.available() < 2) {
    Serial.print("Error!");
  } 
  else 
  {
    raw_sensor_value  = Wire.read() << 8; // read the MSB from the sensor
    raw_sensor_value |= Wire.read();      // read the LSB from the sensor
    sensor_reading = ((int16_t) raw_sensor_value) / ((float) scale_factor);
    if(raw_output)
      Serial.print((int16_t) raw_sensor_value);
    else
      Serial.print(sensor_reading);
    Serial.print("!");
  }
}


// -----------------------------------------------------------------------------
// USB/serial communication routines (Arduino - PC)
// -----------------------------------------------------------------------------

/*
// void serialEvent() does not seem to work with the xiao seeeduino - >Polling of Serial
*/

void decodage_serial() {
  if(buffer_entree[0] == 'M')
  {
    do_measurement(false);
    
  }
  else if (buffer_entree[0] == 'R')
  {
    do_measurement(true);
  }
  else if (buffer_entree[0] == 'I')
  {
    get_sensor_info();
  }
  else if (buffer_entree[0] == '?')
  {
   Serial.print(DEV_ID);
   Serial.print("!");
  }
  else
  {
   Serial.print("?!");
  }

}



/******************************************************************************
	Top-level Arduino code
 ******************************************************************************/

// -----------------------------------------------------------------------------
// Arduino setup routine, just runs once
// -----------------------------------------------------------------------------
void setup() {
  Serial.begin(9600); // initialize serial communication
  Serial.setTimeout(1000); // 1000 ms serial timeout
  Wire.begin();       // join i2c bus (address optional for master)

  get_sensor_info();
}


// -----------------------------------------------------------------------------
// Arduino main loop, loops forever
// -----------------------------------------------------------------------------
void loop() {
  int i;
  // void serialEvent() does not seem to work with the xiao seeeduino - >Polling of Serial
  if (Serial.available() > 0) {
    // empty buffer first!
    for (i = 0; i < BUFFER_ENTREE_LEN; i++)
      buffer_entree[0] = '\0';
    nb_char = Serial.readBytesUntil('!', buffer_entree, max_char);  // see setup() for timeout
    // If the first character is understood, but the '!' termination is missing, 
    // the device will respond after timeout complete...
    // In this case, it is OK, since it guarantuees device to return to a ready
    // state after a defined time
    decodage_serial();
  }
  delay(20);
  //delay(delay_measurement_ms); // milliseconds delay between reads (for demo purposes)
}

