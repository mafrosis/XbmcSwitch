int pushButton = 2;
int switchLed = 13;
int mainLed = 6;

int switchState = 1;

#define ON 49	// 1
#define OFF 48	// 0

void setup(){
	// start serial connection
	Serial.begin(9600);

	// configure pin2 as an input
	pinMode(pushButton, INPUT);
	// turn on pullup resistor
	digitalWrite(pushButton, HIGH);

	// output LED ports
	pinMode(switchLed, OUTPUT); 
	pinMode(mainLed, OUTPUT); 
}

void loop(){
	if (Serial.available() > 0) {
		// read over serial port
		int serialRead = Serial.read();

		// set LED on/off from serial
		if(serialRead == ON) {
			digitalWrite(mainLed, 1);
		}else{
			digitalWrite(mainLed, 0);
		}

		// check for button press
		int sensorRead = digitalRead(pushButton);

		if(switchState != sensorRead) {
			switchState = sensorRead;

			// send on serial when switch pushed
			if(sensorRead == 0) {
				Serial.println(serialRead);
			}
		}

		// write the inverted switch value to the LED
		digitalWrite(switchLed, !sensorRead);

		// introduce a sensible delay
		delay(100);
	}
}
