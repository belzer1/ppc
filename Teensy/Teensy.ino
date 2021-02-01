#define LASER Serial1
#define PC Serial

byte byte0;
byte byte1;
byte byte2;
byte byte3;

int ledPin = 13;
int offsetAnalog = A21;
int offsetFlag = 37;
int flag_range = 120; //GHz
int sweep_range = 0;

void setup() {

  // open serial port to computer
  PC.begin(9600);
  // open serial port to laser
  LASER.begin(9600);

  pinMode(ledPin, OUTPUT);
  pinMode(offsetFlag, OUTPUT);
  digitalWrite(offsetFlag, LOW);

  analogWriteResolution(12);
  analogWrite(offsetAnalog, 2000);
}

void wait_for_laser() {
  while (LASER.available() < 4) {
    delayMicroseconds(1);
  }
}

void pass_on_to_PC() {
  // read bytes from laser and pass onto PC
  byte0 = LASER.read();
  byte1 = LASER.read();
  byte2 = LASER.read();
  byte3 = LASER.read();

  if (byte1 == 228) {
    //intercept sweep range response
    sweep_range = (byte2 << 8) + byte3; //in units of GHz
    sweep_range = sweep_range * 10; //in units of 0.1GHz
  }

  PC.write(byte0);
  PC.write(byte1);
  PC.write(byte2);
  PC.write(byte3);
}

void pass_on_to_LASER() {
  // read bytes from PC and pass onto laser
  byte0 = PC.read();
  byte1 = PC.read();
  byte2 = PC.read();
  byte3 = PC.read();

  if (byte0 + byte1 + byte2 + byte3 == 4 * 255) {
    laser_monitor();
  }

  LASER.write(byte0);
  LASER.write(byte1);
  LASER.write(byte2);
  LASER.write(byte3);
}

void update_offset() {
  LASER.write(128);
  LASER.write(230);
  LASER.write(0);
  LASER.write(0);

  wait_for_laser();

  byte0 = LASER.read();
  byte1 = LASER.read();
  byte2 = LASER.read();
  byte3 = LASER.read();

  // calculate laser offset
  // offset during CleanSweep is encoded as readout*0.1GHz, laser_offset is in units of 0.1GHz
  int laser_offset = (byte2 << 8) + byte3;
  if (laser_offset >= 1 << 15) {
    laser_offset = laser_offset - (1 << 16);
  }

  int analog_offset;
  if (sweep_range == 0) {
    analog_offset = 2048;
  } else {
    analog_offset = (laser_offset * 3072 + sweep_range * 1536) / sweep_range + 512;
  }
  //  write result to analog pin for external monitoring
  analogWrite(offsetAnalog, analog_offset); //max is 4096


  if (laser_offset < 0) {
    digitalWrite(offsetFlag, HIGH);
  } else {
    digitalWrite(offsetFlag, LOW);
  }
}
long t0;
void loop() {
  if (PC.available() >= 4) {
    pass_on_to_LASER();
    wait_for_laser();
    pass_on_to_PC();
  }

    if (LASER.available() + PC.available() == 0) {
      update_offset();
      delay(1);
    }

  //  delay(1);
  //  t0 = micros();
  //  LASER.write(17);
  //  LASER.write(288);
  //  LASER.write(0);
  //  LASER.write(10);
  //  wait_for_laser();
  //  Serial.println(micros()-t0);
  //  delay(1);



}
