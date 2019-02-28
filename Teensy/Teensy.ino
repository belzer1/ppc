dd#define LASER Serial1
#define PC Serial

int byte0;
int byte1;
int byte2;
int byte3;

void setup() {
  
  // open serial port to computer
  PC.begin(9600);
  
  //open serial port to laser
  LASER.begin(19200,SERIAL_8N1);

}

void loop() {
  
  if(PC.available() >= 4){  // read bytes from PC and pass onto laser
    byte0 = PC.read()
    byte1 = PC.read()
    byte2 = PC.read()
    byte3 = PC.read()
    LASER.write(byte0)
    LASER.write(byte1)
    LASER.write(byte2)
    LASER.write(byte3)
  }

  if(LASER.available() >= 4){ // read bytes from PC and pass onto laser
    byte0 = LASER.read()
    byte1 = LASER.read()
    byte2 = LASER.read()
    byte3 = LASER.read()
    PC.write(byte0)
    PC.write(byte1)
    PC.write(byte2)
    PC.write(byte3)
  }

}
