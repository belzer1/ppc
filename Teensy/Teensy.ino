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

void setup() {
  
  // open serial port to computer
  PC.begin(9600);
  // open serial port to laser
  LASER.begin(9600);  

  pinMode(ledPin, OUTPUT);
  pinMode(offsetFlag, OUTPUT);
  digitalWrite(offsetFlag, LOW);
  
  analogWriteResolution(12);
  analogWrite(offsetAnalog,2000);
}

void wait_for_laser(){
  while(LASER.available()<4){
    delayMicroseconds(1);    
  }
}

void pass_on_to_PC() {
   // read bytes from laser and pass onto PC
  byte0 = LASER.read();
  byte1 = LASER.read();
  byte2 = LASER.read();
  byte3 = LASER.read();

//  PC.print(byte0,HEX);
//  PC.print(", ");
//  PC.print(byte1,HEX);
//  PC.print(", ");
//  PC.print(byte2,HEX);
//  PC.print(", ");
//  PC.println(byte3,HEX);

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

  if (byte0+byte1+byte2+byte3 == 4*255){
    laser_monitor();
  }


  LASER.write(byte0);
  LASER.write(byte1);
  LASER.write(byte2);
  LASER.write(byte3);
}

void update_offset() {
  //The sequence of bytes needed to read the frequency offset
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
  // offset during CleanSweep is encoded as (readout - 2000)*0.1GH
  int laser_offset = (byte2 << 8) + byte3;
  if (laser_offset >= 1<<15){
    laser_offset = laser_offset - (1<<16);
  }
  laser_offset = laser_offset + 2000; //this works for CleanSweep
  //  write result to analog pin for external monitoring
  analogWrite(offsetAnalog,laser_offset);

  
  if (abs(laser_offset-2000)<flag_range*10/2){
    digitalWrite(offsetFlag,HIGH);
  } else {
    digitalWrite(offsetFlag,LOW);
  }
}

void loop() {

  if (LASER.available() >= 4){
    pass_on_to_PC();
  } else if (PC.available() >= 4){
    pass_on_to_LASER();
  } 
  //laser typically takes 10ms to reply
  //wait 15ms to make sure laser/PC was no serial message, then update analog scan offset
  delay(15);
  if (LASER.available() + PC.available() == 0){
    update_offset();
  }

  delay(1);  
  
}
