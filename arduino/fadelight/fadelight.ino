/*
  Blink
  Turns on an LED on for one second, then off for one second, repeatedly.
 
  This example code is in the public domain.
 */
 
// Pin 13 has an LED connected on most Arduino boards.
// give it a name:
int led = 9;

// the setup routine runs once when you press reset:
void setup() {                
  // initialize the digital pin as an output.
  pinMode(led, OUTPUT);     
}

// the loop routine runs over and over again forever:
void loop() {
  for (int fadeValue = 0; fadeValue <= 255; fadeValue +=5) {
    analogWrite(led, fadeValue);   // turn the LED on (HIGH is the voltage level)
    delay(30);               // wait for a second
  }  
  for (int fadeValue = 255; fadeValue >= 0; fadeValue -=5) {
    analogWrite(led, fadeValue);   // turn the LED on (HIGH is the voltage level)
    delay(30);               // wait for a second
  }
}
