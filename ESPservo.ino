#include <Servo.h> //Bibliotek for kontroll av servo

static const int SluseServoPin = 32;
static const int SortServoPin = 12;
const int inputbit0 = 26;
const int inputbit1 = 27;
Servo servoSluse;
Servo servoSort;

int currentAngleSluse = 0;
int currentAngleSortering = 0;

int controllvalue;
int bit0;
int bit1;

int casevalue = 0;
unsigned long interval = 1000;
unsigned long currentMillis;
unsigned long previousMillis;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  servoSluse.attach(SluseServoPin);
  servoSort.attach(SortServoPin);
  pinMode(inputbit0, INPUT);
  pinMode(inputbit1, INPUT);
  sluse(0);
  sortering(0);
  controllvalue = 0;
  
}

void loop() {
  //finner hvilken oppgave (case) som skal utføres
  vent(1);
  bit0 = digitalRead(inputbit0);
  bit1 = digitalRead(inputbit1);
  casevalue = bit0 + 2 * bit1;
  
  if (casevalue != controllvalue) {
    controllvalue = casevalue;
    switch (casevalue) {
      case 1: //papp
        Serial.print("papp");
        servo_og_tid(1500, 180, 0);
        servo_og_tid(200, 0, 0);
        break;

      case 2: //plast
        Serial.print("plast");
        servo_og_tid(1500, 180, 80);
        servo_og_tid(200, 0, 0);
        break;
      case 3: //annet
        Serial.print("annet");
        servo_og_tid(1500, 180, 160);
        servo_og_tid(200, 0, 0);
        break;

      default:
        Serial.print("ingeiting\n");
        break;
    }
  }
}


//funksjon for justering av sorteringsservo
void sortering(int vinkel) {
  servoSort.write(vinkel);
}
//funksjon for justering av sluseservo
void sluse(int vinkel) {
  servoSluse.write(vinkel);
}
//Funkskon for tid
void vent(int interval) {
  currentMillis = millis();
  previousMillis = millis();
  while (currentMillis - previousMillis <= interval) {
    currentMillis = millis();
  }
}

void servo_og_tid(int tid, int sluseV, int sorteringV) {
  currentMillis = millis();
  previousMillis = millis();

  while (abs(sorteringV - currentAngleSortering)!= 0) {
    if(currentAngleSortering <= sorteringV){
      currentAngleSortering += 1;
    }
    else{
      currentAngleSortering -= 1;
    }
    sortering(currentAngleSortering);
    vent(2); 
   
  }
  Serial.print(" sort ferdig \n");
  
  while (abs(sluseV - currentAngleSluse)!= 0) {
    if(currentAngleSluse <= sluseV){
      currentAngleSluse += 1;
    }
    else{
      currentAngleSluse -= 1;
    }
    sluse(currentAngleSluse);
    vent(2);
  }

  Serial.print(" servoferdig \n");
  while (currentMillis - previousMillis <= tid) {
    currentMillis = millis();

  }


}