unsigned long previousMillis = 0; 
const long update_period = 500;


void laser_monitor(){
  while (PC.available()==0){
    //look at current time
    unsigned long currentMillis = millis();
    
    // if an update_period has passed, update PC with status
    if (currentMillis - previousMillis >= update_period){
      previousMillis = currentMillis;
  
      // Do a full status check, passing onto PC for each measurement
      probe_power();
      probe_temperature();
      probe_current();
      probe_offset();
      probe_scan();
    } 
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

void probe_offset() {
  //The sequence of bytes needed to read the frequency offset
  LASER.write(128);
  LASER.write(230);
  LASER.write(0);
  LASER.write(0);

  wait_for_laser();
  //pass on bytes of laser power
  pass_on_to_PC();
}

boolean probe_scan() {
  //The sequence of bytes needed to read scan status
  LASER.write(176);
  LASER.write(229);
  LASER.write(0);
  LASER.write(0);

  wait_for_laser();
  //pass on bytes of laser power
  pass_on_to_PC();
}
