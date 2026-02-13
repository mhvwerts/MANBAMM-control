#define PIN_A 5
#define PIN_B 6
#define MON_A 7
#define MON_B 8
#define LOWDLY 100
#define VALVEDLY 900
#define LOOPDLY 100


void setup() {
  // put your setup code here, to run once:
  pinMode(PIN_A, OUTPUT);
  digitalWrite(PIN_A, LOW);

  pinMode(PIN_B, OUTPUT);
  digitalWrite(PIN_B, LOW);

  Serial.begin(9600); // initialize serial comms, default = 8N1
  Serial.setTimeout(1000);
  while (Serial.available()) Serial.read();
}


void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    char c = Serial.read(); 
    // only take first character, rest will be flushed to avoid delayed axecution of piled up instructions
    switch (c) {
      case 'a':
        // do something
        digitalWrite(PIN_A, HIGH);
        delay(LOWDLY);
        digitalWrite(PIN_A, LOW);
        Serial.write('A');
        delay(VALVEDLY);
        break;
      case 'b':
        // do something else
        digitalWrite(PIN_B, HIGH);
        delay(LOWDLY);
        digitalWrite(PIN_B, LOW);
        Serial.write('B');
        delay(VALVEDLY);
        break;
      default:
        break;
    }
    delay(LOOPDLY); // just wait (0.1) seconds
    // flush RX buffer
    while (Serial.available()) Serial.read();
  }
}
