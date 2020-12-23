// Include the AccelStepper Library
#include <AccelStepper.h>

// Define step constants
#define FULLSTEP 4
#define HALFSTEP 8

// Creates two instances
// Pins entered in sequence IN1-IN3-IN2-IN4 for proper step sequence
AccelStepper stepper1(HALFSTEP, 10,12, 11, 13);
AccelStepper stepper2(HALFSTEP, 5, 3, 4, 2);
AccelStepper stepper3(HALFSTEP, 6, 8, 7, 9);
//AccelStepper stepper3(HALFSTEP, A2, A4, A3, A5);


void setup() {
  Serial.begin(9600);
  Serial.println("Stepper Controller Online!");

  stepper1.setMaxSpeed(1000.0);
  stepper1.setAcceleration(40.0);
  stepper1.setSpeed(1);
  //stepper1.moveTo(-203800);

  stepper2.setMaxSpeed(1000.0);
  stepper2.setAcceleration(40.0);
  stepper2.setSpeed(1);
  //stepper2.moveTo(-203800);

  stepper3.setMaxSpeed(1000.0);
  stepper3.setAcceleration(40.0);
  stepper3.setSpeed(1);
  //stepper3.moveTo(-203800);
}

void loop() {
  uint8_t i;
  if (Serial.available() > 3) {
    byte motor = Serial.read();
    byte int1 = Serial.read();
    byte int256 = Serial.read();
    byte int65536 = Serial.read();
    int motor_in = (int)motor;
    long int1_in = (long)int1;
    long int256_in = (long)int256;
    long int65536_in = (long)int65536;
    int sign = 1;
    if bitRead(motor,4){
      sign = -1;
    }
    
    long steps = (int65536 * 65536 + int256 * 256 + int1) * sign;
    
   if bitRead(motor,1){
      stepper1.moveTo(steps);
    }
   if bitRead(motor,2){
      stepper2.moveTo(steps);
    }
   if bitRead(motor,3){
      stepper3.moveTo(steps);
    }
 
  }

  // Move the motor one step
  stepper1.run();
  stepper2.run();
  stepper3.run();
}
