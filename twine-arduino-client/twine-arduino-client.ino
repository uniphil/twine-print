#include <SoftwareSerial.h>

#define BUTTON_0 2
#define BUTTON_1 3
#define BUTTON_2 4
#define BUTTON_3 5

#define DEBOUNCE 300

SoftwareSerial Thermal(10, 9);

void setup() {
  Serial.begin(9600);
  Thermal.begin(19200);
  pinMode(BUTTON_0, INPUT_PULLUP);
  pinMode(BUTTON_1, INPUT_PULLUP);
  pinMode(BUTTON_2, INPUT_PULLUP);
  pinMode(BUTTON_3, INPUT_PULLUP);
  pinMode(8, OUTPUT);
  digitalWrite(8, LOW);  // fake ground
}

unsigned long last_press = 0;
void handle_button() {
  unsigned long now = millis();
  if (now < last_press + DEBOUNCE) {
    return;
  }
  char button;
  if (!digitalRead(BUTTON_0)) {
    button = '0';
  } else if (!digitalRead(BUTTON_1)) {
    button = '1';
  } else if (!digitalRead(BUTTON_2)) {
    button = '2';
  } else if (!digitalRead(BUTTON_3)) {
    button = '3';
  } else {
    return;
  }
  last_press = now;
  Serial.write(button);
}


void handle_serial_in() {  
  if (Serial.available() > 0) {
    byte b = Serial.read();
    Thermal.write(b);
  }
}

void loop() {
  handle_button();
  handle_serial_in();
}
