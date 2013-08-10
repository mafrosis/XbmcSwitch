int pushButton = 2;
int mainLed = 3;

int switchState = 1;
int noSerialCount = 0;

#define ON 49	// 1
#define OFF 48	// 0

void setup(){
	// start serial connection
	Serial.begin(9600);

	// configure pin2 as an input
	pinMode(pushButton, INPUT);
	// turn on pullup resistor
	digitalWrite(pushButton, HIGH);

	// output port for LED
	pinMode(mainLed, OUTPUT); 
}

void loop(){
	int serialRead = -1;

	if (Serial.available() > 0) {
		// read over serial port
		serialRead = Serial.read();

		// set LED on/off from serial
		if(serialRead == ON) {
			digitalWrite(mainLed, 1);
		}else{
			digitalWrite(mainLed, 0);
		}

		noSerialCount = 0;
	}else{
		noSerialCount += 1;

		// if no serial input for 2 seconds, switch off LED
		if(noSerialCount == 20) {
			digitalWrite(mainLed, 0);
		}
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

	// introduce a sensible delay
	delay(100);
}
