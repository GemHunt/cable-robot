# cable-robot
This project is a very low cost way of getting images small parts with random camera poses.

It's a $10 three string cable robot that carries a camera over a horizontal HD display showing Aruco markers. The markers are tiny at 8x8 pixels. The strings are controlled with 28BYJ-48 steppers using UNL2003A boards on an Arduino. 
 
This bounces around and takes 10-20 seconds to stabilize.
 
Positioning is not very good at say 1-5mm, depending on how hard you try. 
 
Once it does stabilize you can get 3D pose very accurately. 

![Cable Robot](cable-robot.jpg "Cable Robot")

Open the serial port:
sudo usermod -a -G dialout $USER

  
