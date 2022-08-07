#include "Adafruit_Thermal.h"

#include "SoftwareSerial.h"
#define TX_PIN 6 // RX on printer
#define RX_PIN 5 // TX on printer

SoftwareSerial mySerial(RX_PIN, TX_PIN); 
Adafruit_Thermal printer(&mySerial);

String message;

void setup() {
 Serial.begin(9600);
 mySerial.begin(9600);  
 printer.begin();
 printer.setFont('A');
 printer.boldOn();
 printer.println("Printer initialized");
 printer.feed(2);

}

void loop() {
 while (!Serial.available());
 message = Serial.readString();
 if (message == "Marco"){
  Serial.println("Polo") ;
 }
 else{
  Serial.println(message) ;
   if (message.length() > 0){
     printer.print(message);
     printer.feed(1);
  }
 }
}
