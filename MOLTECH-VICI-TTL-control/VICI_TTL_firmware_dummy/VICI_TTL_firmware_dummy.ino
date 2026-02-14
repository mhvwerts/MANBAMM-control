/* 
    specially adapted "dummy" firmware for development purposes
    does not require a VICI valve actuator to be physically attached to the Arduino

    imitates "trouble-free" (ideal) operation    
*/

#define PIN_A 5
#define PIN_B 6
#define MON_A 7
#define MON_B 8
#define PULSEDLY 100
#define VALVEDLY 300
#define LOOPDLY 100

int stateAB = 2;  // imitate initial position at B

void setup() {
  // Configure and initialize pins
  pinMode(PIN_A, OUTPUT);
  digitalWrite(PIN_A, LOW);
  pinMode(PIN_B, OUTPUT);
  digitalWrite(PIN_B, LOW);
  pinMode(MON_A, INPUT);
  pinMode(MON_B, INPUT);

  Serial.begin(9600); // initialize serial comms, default = 8N1
  Serial.setTimeout(1000);
  while (Serial.available()) Serial.read();
}


void output_status() {
  // int stateAB = (digitalRead(MON_B) << 1) | digitalRead(MON_A);
  switch (stateAB) {
    case 0:
      Serial.write('0');
      break;
    case 1:
      Serial.write('A');
      break;
    case 2:
      Serial.write('B');
      break;
    case 3:
      Serial.write('X');
      break;
    default:
      // should never happen!
      Serial.write('?');
      break;
  }
}


void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read(); 
    // only take first character, rest will be flushed to avoid delayed execution of piled up instructions
    switch (c) {
      case 'a':
        // digitalWrite(PIN_A, HIGH);
        delay(PULSEDLY);
        stateAB = 1;
        // digitalWrite(PIN_A, LOW);
        delay(VALVEDLY);
        output_status();
        break;
      case 'b':
        // digitalWrite(PIN_B, HIGH);
        delay(PULSEDLY);
        stateAB = 2;
        // digitalWrite(PIN_B, LOW);
        delay(VALVEDLY);
        output_status();
        break;
      case '?':
        output_status();
        break;
      case '!':
        // The output string should end with an exclamation mark, and should
        // not contain any other exclamation marks.
        Serial.print("Hello, this is MOLTECH-VICI-TTL control v260213a (dummy firmware)!");
        break;
      default:
        break;
    }
    delay(LOOPDLY); // just wait LOOPDLY milliseconds
    // flush RX buffer
    while (Serial.available()) Serial.read();
  }
}
