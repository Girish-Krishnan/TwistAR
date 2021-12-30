/*
 * Initialize the various components of the wearable
 */
int ax = 0; int ay = 0; int az = 0;
int sampleTime = 0; // Time of last sample (in Sampling tab)
bool sending;
int redLED = 16;
int greenLED = 17;
int blueLED = 19;
int yellowLED = 21;
int state = 1;
// state = 1 new one
// state = -1 full requirements
String LH_COL = "Free";
String RH_COL = "Free";
String LL_COL = "Free";
String RL_COL = "Free";
String newLimb = "None";
String newColor = "None";
String levelNum = "0";
String level = "0";
int ax_arr[100], ay_arr[100], az_arr[100];
int ax_sum, ay_sum, az_sum;
int ax_avg, ay_avg, az_avg;
unsigned long int timeTilted = 0;


void setup() {
  setupAccelSensor();
  setupCommunication();
  setupDisplay();
  sending = false;
  writeDisplay("TwistAR", 0, true);
  pinMode(redLED, OUTPUT);
  pinMode(greenLED, OUTPUT);
  pinMode(blueLED, OUTPUT);
  pinMode(yellowLED, OUTPUT);
  writeDisplay("Calibrating...",1,true);
  writeDisplay("HOLD STILL",2,false);
  int i;
  for(i = 0; i < 100; i++) {
    readAccelSensor();
    ax_arr[i] = ax;
    ay_arr[i] = ay;
    az_arr[i] = az;
    delay(50);
  }
  for(i = 0; i < 100; i++) {
    ax_sum += ax_arr[i];
    ay_sum += ay_arr[i];
  }
  ax_avg = (int)(ax_sum/100);
  ay_avg = (int)(ay_sum/100);
  az_avg = (int)(az_sum/100);
  digitalWrite(redLED, HIGH);
  delay(1000);
  digitalWrite(greenLED, HIGH);
  delay(1000);
  digitalWrite(blueLED, HIGH);
  delay(1000);
  digitalWrite(yellowLED, HIGH);
  delay(1000);
  digitalWrite(yellowLED, LOW);
  digitalWrite(blueLED, LOW);
  digitalWrite(greenLED, LOW);
  digitalWrite(redLED, LOW);
}

/*
 * The main processing loop
 */
void loop() {
  String command = receiveMessage();
  readAccelSensor();
  Serial.println(String(ax) + " " + String(ay) + " " + String(az));  
  delay(100);

  if((millis() - timeTilted > 300) && (getOrientation() == 1)) {
    state = -state;
  }
 
  if(command == "sleep") {
    sending = false;
    
  }
  else if(command == "wearable") {
    sending = true;
    writeDisplay("Wearable", 0, true);
  }
  else if(command == "testing") {
    sending = true;
    writeDisplay("Testing", 0, true);
  }
  else if (command.substring(0, 1) == "!"){
    sending = true;
    String limb = command.substring(1, 3);
    String color = command.substring(3, 4);
    levelNum = command.substring(4, 5);
    newLimb = limb;
    if (color == "R"){
      color = "red";
      digitalWrite(redLED, HIGH);
      digitalWrite(greenLED, LOW);
      digitalWrite(blueLED, LOW);
      digitalWrite(yellowLED, LOW);
    }
    else if (color == "G"){
      color = "green";
      digitalWrite(redLED, LOW);
      digitalWrite(greenLED, HIGH);
      digitalWrite(blueLED, LOW);
      digitalWrite(yellowLED, LOW);
    }
    else if (color == "B"){
      color = "blue";
      digitalWrite(redLED, LOW);
      digitalWrite(greenLED, LOW);
      digitalWrite(blueLED, HIGH);
      digitalWrite(yellowLED, LOW);
    }
    else if (color == "Y"){
      color = "yellow";
      digitalWrite(redLED, LOW);
      digitalWrite(greenLED, LOW);
      digitalWrite(blueLED, LOW);
      digitalWrite(yellowLED, HIGH);
    }
    newColor = color;
    if (limb == "RH"){
      RH_COL = color;
    }
    else if (limb == "LH"){
      LH_COL = color;
    }
    else if (limb == "RL"){
      RL_COL = color;
    }
    else if (limb == "LL"){
      LL_COL = color;
    }
  }
  if(sending && sampleSensors()) {
    String response = String(sampleTime) + ",";
    response += String(ax) + "," + String(ay) + "," + String(az);
    sendMessage(response);
  }
  if (state == 1){
    String newCommand = newLimb + " on " + newColor;
    String level = "Level: " + String(levelNum);
    writeDisplay("NEW!", 0, true);
    writeDisplay(newCommand.c_str(), 1, true);
    writeDisplay(level.c_str(), 3, true);
  }
  if (state == -1){
    //oled.clearDisplay(); // clear old display
    String leftHand = "LH: " + LH_COL;
    String rightHand = "RH: " + RH_COL;
    String leftLeg = "LL: " + LL_COL;
    String rightLeg = "RL: " + RL_COL;
    writeDisplay(leftHand.c_str(), 0, true);
    writeDisplay(rightHand.c_str(), 1, true);
    writeDisplay(leftLeg.c_str(), 2, true);
    writeDisplay(rightLeg.c_str(), 3, true);
  }
}
