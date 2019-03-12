#define LASER Serial1
#define PC Serial

int byte0;
int byte1;
int byte2;
int byte3;

int laser_power;
int laser_temperature;
int case_temperature;
int laser_current;
int TEC_current;
int freq_offset;
int scan_status;

const long update_period = 500;

boolean scanning = false;

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

void monitor_scan(){
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= update_period){
    previousMillis = currentMillis;

    // Do a full status check and send to PC
    probe_power(&laser_power);
    probe_temperature(&laser_temperature, &case_temperature);
    probe_current(&laser_current, &TEC_current);
    probe_scan(&scan_status);
  }
  
  probe_offset();
  
  }
  
}

void wait_for_laser(){
  while(LASER.available()<4){
    delay(1);    
  }
}

int probe_power(int* a) {
  //The sequence of bytes needed to request the frequency offset
  LASER.write(96);
  LASER.write(66);
  LASER.write(0);
  LASER.write(0);

  wait_for_laser();

  byte0 = LASER.read();
  byte1 = LASER.read();
  byte2 = LASER.read();
  byte3 = LASER.read();

  *a = (byte2 << 8) + byte3;
}

int probe_temperature(int* a, int* b) {
  //The sequence of bytes needed to request AEA
  LASER.write(208);
  LASER.write(88);
  LASER.write(0);
  LASER.write(0);

  wait_for_laser();
    
  byte0 = LASER.read();
  byte1 = LASER.read();
  byte2 = LASER.read();
  byte3 = LASER.read();

  //The sequence of bytes needed to request AEA
  LASER.write(176);
  LASER.write(11);
  LASER.write(0);
  LASER.write(0);

  while(LASER.available()<4){
    delay(1);
  }
    
  byte0 = LASER.read();
  byte1 = LASER.read();
  byte2 = LASER.read();
  byte3 = LASER.read();
  *a = (byte2 << 8) + byte3;

  LASER.write(176);
  LASER.write(11);
  LASER.write(0);
  LASER.write(0);

  wait_for_laser();
    
  byte0 = LASER.read();
  byte1 = LASER.read();
  byte2 = LASER.read();
  byte3 = LASER.read();  
  *b = (byte2 << 8) + byte3;

  
}

void probe_current(int* a, int* b) {
  //The sequence of bytes needed to request AEA
  LASER.write(66);
  LASER.write(87);
  LASER.write(0);
  LASER.write(0);

  wait_for_laser();
    
  byte0 = LASER.read();
  byte1 = LASER.read();
  byte2 = LASER.read();
  byte3 = LASER.read();

  //The sequence of bytes needed to request the frequency offset
  LASER.write(176);
  LASER.write(11);
  LASER.write(0);
  LASER.write(0);

  wait_for_laser();
    
  byte0 = LASER.read();
  byte1 = LASER.read();
  byte2 = LASER.read();
  byte3 = LASER.read();
  *a = (byte2 << 8) + byte3;

  LASER.write(176);
  LASER.write(11);
  LASER.write(0);
  LASER.write(0);
  
  wait_for_laser();
    
  byte0 = LASER.read();
  byte1 = LASER.read();
  byte2 = LASER.read();
  byte3 = LASER.read();
  *b = (byte2 << 8) + byte3;  
}

void probe_scan() {
  //The sequence of bytes needed to request AEA
  LASER.write(176);
  LASER.write(229);
  LASER.write(0);
  LASER.write(0);

  wait_for_laser();
    
  byte0 = LASER.read();
  byte1 = LASER.read();
  byte2 = LASER.read();
  byte3 = LASER.read();  
}

void probe_offset() {
  //The sequence of bytes needed to request the frequency offset
  LASER.write(128);
  LASER.write(230);
  LASER.write(0);
  LASER.write(0);

  wait_for_laser();
    
  byte0 = LASER.read();
  byte1 = LASER.read();
  byte2 = LASER.read();
  byte3 = LASER.read();

//  write result to analog pin for external monitoring  
  int laser_offset = (byte2 << 8) + byte3;
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

  if(byte1 == 255){
    scanning = true;
    digitalWrite(ledPin, HIGH);
  } else if(byte1 == 254) {
    scanning = false;
    digitalWrite(ledPin, LOW);
  } else if(byte1 == 253) {
    probe_offset();
  }  
    else {  
    LASER.write(byte0);
    LASER.write(byte1);
    LASER.write(byte2);
    LASER.write(byte3);
  }
}


void loop() {

  unsigned long currentMillis = millis();

//  if(LASER.available() >= 4){
//    pass_on_to_PC();
//  }

//  if(scanning){
//    probe_offset();
//    delay(100);
//  }
//  
  if(PC.available() >= 4){
    PC.println('asdsadsad');
    monitor_scan();
    PC.println(laser_power);
    PC.println(laser_temperature);
    PC.println(case_temperature);
    PC.println(laser_current);
    PC.println(TEC_current);

//    pass_on_to_LASER();
  }
  
  delay(10);

}



