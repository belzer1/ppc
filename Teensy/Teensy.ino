#define LASER Serial1
#define PC Serial

int byte0;
int byte1;
int byte2;
int byte3;

unsigned long previousMillis = 0; 
const long update_period = 100;

boolean scanning = false;

int ledPin = 13;

void setup() {
  
  // open serial port to computer
  PC.begin(9600);
  
  //open serial port to laser
  LASER.begin(9600);

  pinMode(ledPin, OUTPUT);
  
  analogWriteResolution(12);
}

void wait_for_laser(){
  while(LASER.available()<4){
    delay(1);    
  }
}

void scan_monitor(){
  //look at current time
  unsigned long currentMillis = millis();

  // if it's been an update_period has passed, update PC with status
  if (currentMillis - previousMillis >= update_period){
    previousMillis = currentMillis;

    // Do a full status check, passing onto PC for each measurement
    probe_power();
    probe_temperature();
    probe_current();
    probe_offset(true);
    scanning = probe_scan();
  } else {	//else just do a offset read and write it to the analog output for external monitoring
  	probe_offset(false);
  }
}

void probe_power() {
  //The sequence of bytes needed to read the frequency offset
  LASER.write(96);
  LASER.write(66);
  LASER.write(0);
  LASER.write(0);

  wait_for_laser();
  //pass on bytes of laser power
  pass_on_to_PC();
}

void probe_temperature() {
  //The sequence of bytes needed to read the laser temperatures, returned as AEA
  LASER.write(208);
  LASER.write(88);
  LASER.write(0);
  LASER.write(0);

  wait_for_laser();
    
  LASER.read();
  LASER.read();
  LASER.read();
  LASER.read();

  //The sequence of bytes needed to read AEA
  LASER.write(176);
  LASER.write(11);
  LASER.write(0);
  LASER.write(0);

  wait_for_laser();
  //pass on bytes of laser temperature
  pass_on_to_PC();

  //The sequence of bytes needed to read AEA
  LASER.write(176);
  LASER.write(11);
  LASER.write(0);
  LASER.write(0);

  wait_for_laser();
  // pass on the bytes of case temperature
  pass_on_to_PC();
}

void probe_current() {
  //The sequence of bytes needed to read the laser temperatures, returned as AEA
  LASER.write(66);
  LASER.write(87);
  LASER.write(0);
  LASER.write(0);

  wait_for_laser();
    
  LASER.read();
  LASER.read();
  LASER.read();
  LASER.read();

  //The sequence of bytes needed to read AEA
  LASER.write(176);
  LASER.write(11);
  LASER.write(0);
  LASER.write(0);

  wait_for_laser();
  //pass on bytes of gain chip current
  pass_on_to_PC();
  

  //The sequence of bytes needed to read AEA
  LASER.write(176);
  LASER.write(11);
  LASER.write(0);
  LASER.write(0);
  
  wait_for_laser();
  //pass on bytes of TEC current    
  pass_on_to_PC();
}

boolean probe_scan() {
  //The sequence of bytes needed to read scan status
  LASER.write(176);
  LASER.write(229);
  LASER.write(0);
  LASER.write(0);

  wait_for_laser();
  // pass on bytes of scan status
  byte0 = LASER.read();
  byte1 = LASER.read();
  byte2 = LASER.read();
  byte3 = LASER.read();  
  PC.write(byte0);
  PC.write(byte1);
  PC.write(byte2);
  PC.write(byte3);
  boolean ret;
  
  if (byte3 % 2 == 0){
    ret = false;
  } else {
    ret = true;
  }

  return ret;
  
}

void probe_offset(boolean pass_on) {
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
  // pass on bytes of frequency offset
  if (pass_on){
    PC.write(byte0);
    PC.write(byte1);
    PC.write(byte2);
    PC.write(byte3);
  }

  // calculate laser offset, encoding as ##### TO DO
  int laser_offset = (byte2 << 8) + byte3;
  //  write result to analog pin for external monitoring
  analogWrite(A22,laser_offset);
}

void pass_on_to_PC() {
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

void pass_on_to_LASER() {
   // read bytes from PC and pass onto laser
  byte0 = PC.read();
  byte1 = PC.read();
  byte2 = PC.read();
  byte3 = PC.read();

  if(byte1 == 255){ //the signal to start scan monitor mode
    scanning = true;
  } else if(byte1 == 254) { //the signal to stop scan monitor mode
    scanning = false;
  } else {  
    LASER.write(byte0);
    LASER.write(byte1);
    LASER.write(byte2);
    LASER.write(byte3);
  }
}

void loop() {

  if (LASER.available() >= 4){
    pass_on_to_PC();
  } else if (PC.available() >= 4){
    scanning = false;
    pass_on_to_LASER();
  } else if (scanning){
    scan_monitor();
    delay(1);
  }

  if(scanning){
    digitalWrite(ledPin, HIGH);
    } else {
      digitalWrite(ledPin, LOW);
  }

  delay(1);  
  
}
