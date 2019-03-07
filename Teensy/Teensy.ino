#define LASER Serial1
#define PC Serial

int byte0;
int byte1;
int byte2;
int byte3;

boolean read_once = false;

int ledPin = 13;

unsigned long previousMillis = 0; 

void setup() {
  
  // open serial port to computer
  PC.begin(9600);
  
  //open serial port to laser
  LASER.begin(9600);

  pinMode(ledPin, OUTPUT);
  
  analogWriteResolution(12);
}

void probe_offset() {
  //The sequence of bytes needed to request the frequency offset
  delay(10);
  LASER.write(128);
  LASER.write(230);
  LASER.write(0);
  LASER.write(0);

  while(LASER.available()<4){
    delay(1);
  }
    
  byte0 = LASER.read();
  byte1 = LASER.read();
  byte2 = LASER.read();
  byte3 = LASER.read();
  
  int laser_offset = (byte2 << 8) + byte3;

  analogWrite(A22,laser_offset);
}

void pass_on_LASER() {
   // read bytes from laser and pass onto PC
  byte0 = LASER.read();
  byte1 = LASER.read();
  byte2 = LASER.read();
  byte3 = LASER.read();
  PC.write(byte0);
  PC.write(byte1);
  PC.write(byte2);
  PC.write(byte3);
}

void pass_on_PC() {
   // read bytes from PC and pass onto laser
    byte0 = PC.read();
    byte1 = PC.read();
    byte2 = PC.read();
    byte3 = PC.read();
    if(byte1 == 230){
      read_once = true;
      digitalWrite(ledPin, HIGH);
    }
    LASER.write(byte0);
    LASER.write(byte1);
    LASER.write(byte2);
    LASER.write(byte3);
}


void loop() {

  unsigned long currentMillis = millis();

  if(LASER.available() >= 4){
    pass_on_LASER();
  }

//  if((LASER.available() + PC.available() == 0) && read_once){
//    probe_offset();
//    delay(50);
//  }
  
  if(PC.available() >= 4){
    pass_on_PC();
  }
  
  delay(10);

}


