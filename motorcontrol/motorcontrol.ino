  
// Adafruit Motor shield library
// copyright Adafruit Industries LLC, 2009
// this code is public domain, enjoy!

#include <AFMotor.h>

AF_DCMotor motor1(1);
AF_DCMotor motor2(2);
AF_DCMotor motor3(3);
AF_DCMotor current_motor(1);
byte motor;  
byte command;  
  
void setup() {
  Serial.begin(9600);           // set up Serial library at 9600 bps
  Serial.println("Motor test!");

  // turn on motor
  motor1.setSpeed(30);
  motor1.run(RELEASE);
  motor2.setSpeed(30);
  motor2.run(RELEASE);
  motor3.setSpeed(30);
  motor3.run(RELEASE);
}


void set_dir() {
  if bitRead(command,1){
     current_motor.run(FORWARD);
     Serial.print("FORWARD");
    }
  if bitRead(command,2){
     current_motor.run(BACKWARD);
     Serial.print("BACKWARD");
    }
   if bitRead(command,3){
     current_motor.run(RELEASE);
     Serial.print("RELEASE");
    }
}


void loop() {
  uint8_t i;
  motor = 0;
  command = 0;
  if (Serial.available() > 1) {
    motor = Serial.read();
    command = Serial.read();
    int motor_out = (int)motor;
    int command_out = (int)command;
    Serial.print(motor_out,command_out);
  }
  
  if bitRead(motor,1){
    current_motor = motor1;
   Serial.print("motor1");
   set_dir();
  }
  if bitRead(motor,2){
    current_motor = motor2;
    Serial.print("motor2");
    set_dir();
  }
  if bitRead(motor,3){
    current_motor = motor3;
    Serial.print("motor3");
    set_dir();
  }
  
  



//  Serial.print(input);
//  if (input = 1) {
//    motor1.run(FORWARD);
//  }
//  
//  if (input = 2) {
//    motor1.run(BACKWARD);
//  }
    
  //motor1.run(RELEASE);
  //delay(100);
}
