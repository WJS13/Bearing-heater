#include <LiquidCrystal_I2C.h> 
LiquidCrystal_I2C lcd(0x27, 16, 2); 
int Vo;
float R1 = 100000;              
float logR2, R2, TEMPERATURA1;
float c1 = 2.114990448e-03, c2 = 0.3832381228e-04, c3 = 5.228061052e-07;

int relayPin = 4;

void setup() {
  Serial.begin(9600); 
  lcd.init();
  lcd.clear();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.display();
  
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);
}

void loop() {
  Vo = analogRead(A0);
  R2 = R1 * (1023.0 / (float)Vo - 1.0);
  logR2 = log(R2);
  TEMPERATURA1 = (1.0 / (c1 + c2*logR2 + c3*logR2*logR2*logR2));
  TEMPERATURA1 = TEMPERATURA1 - 273.15;

  Serial.print("Temp.: ");
  Serial.print(TEMPERATURA1);
  Serial.println(" C"); 
  
  lcd.setCursor(0,0);
  lcd.print("T.rodaje: ");  
  lcd.print(TEMPERATURA1);
  lcd.print("C"); 
  
  if (Serial.available() > 0) {
    char comando = Serial.read(); 
    if (comando == '1') {  
      digitalWrite(relayPin, HIGH);
    }
    else if (comando == '0') {  
      digitalWrite(relayPin, LOW);
    }
  }

  delay(1000);
}

