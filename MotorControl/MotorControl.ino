#include <limits.h>
#define INF ULONG_MAX

// Pin fasi motori assi X e Y
const int phaseX1 = 9;
const int phaseX2 = 10;
const int phaseX3 = 11;
const int phaseY1 = 5;
const int phaseY2 = 6;
const int phaseY3 = 7;

// Pin collegato al terminale di accensione dell'alimentatore
const int powerPin = 13;

// Variabili accumulatori per il controllo della frequenza d'incremento PWM
unsigned long timeMotorX = 0, timeMotorY = 0, timeNow = 0;

// Periodi d'incremento PWM per i due motori
unsigned long periodMotorX = INF, periodMotorY = INF;

// Valore di PWM attuale delle 3 fasi dei 2 motori
int pwmX1, pwmX2, pwmX3, pwmY1, pwmY2, pwmY3;

// Direzioni degli incrementi dei pwm delle fasi (1 = crescente, -1 = decrescente)
int signX1, signX2, signX3, signY1, signY2, signY3;

// Direzione di rotazione dei motori (1 = orario, -1 = antiorario) 
int directionX = 1, directionY = 1;

// Buffer ricezione delle due velocità di rotazione da settare
byte serialBuffer[2];

// Variabile di controllo dell'alimentazione del sistema
bool wasRunning = false;

void setup() {
  Serial.begin(9600);
  pinMode(phaseX1, OUTPUT); 
  pinMode(phaseX2, OUTPUT); 
  pinMode(phaseX3, OUTPUT);
  pinMode(phaseY1, OUTPUT); 
  pinMode(phaseY2, OUTPUT); 
  pinMode(phaseY3, OUTPUT);
  pinMode(powerPin, INPUT);

  // Valori iniziali dei PWM delle fasi, sfasate di 120°
  pwmX1 = pwmY1 = 0;
  pwmX2 = pwmY2 = 170;
  pwmX3 = pwmY3 = 170;

  // Direzioni di incremento iniziali dei valori di PWM
  signX1 = signY1 = 1;
  signX2 = signY2 = 1;
  signX3 = signY3 = -1;
}

void loop() {

  // Contro dello stato di alimentazione del sistema
  checkIfRunning();
  
  // Lettura dal seriale delle due velocità di rotazione da settare 
  readVelocities();

  // Esecuzione di nextPWM su tutte e tre le fasi di un motore se è passato un tempo uguale al periodo settato
  timeNow = micros();
  if (timeNow - timeMotorX > periodMotorX) {
    nextPWM(pwmX1, signX1, directionX);
    nextPWM(pwmX2, signX2, directionX);
    nextPWM(pwmX3, signX3, directionX);
    timeMotorX = timeNow;
  }
  if (timeNow - timeMotorY > periodMotorY) {
    nextPWM(pwmY1, signY1, directionY);
    nextPWM(pwmY2, signY2, directionY);
    nextPWM(pwmY3, signY3, directionY);
    timeMotorY = timeNow;
  }

  // Settaggio dei valori di PWM calcolati sui pin
  writePWMs();
}

// Porta il motore dell'asse Y alla posizione iniziale
void initialPosition() {
  for (int i = 0; i < 765; i++) {
    nextPWM(pwmY1, signY1, -1);
    nextPWM(pwmY2, signY2, -1);
    nextPWM(pwmY3, signY3, -1);
    writePWMs();
    delayMicroseconds(1000);
  }
  delay(200);
}

// Controlla se è appena stata data alimentazione ai motori, nel caso esegue initialPosition()
void checkIfRunning() {

  // Controllo dello stato di powerPin, connesso al terminale di accensione dell'alimentatore
  bool isRunning = !digitalRead(powerPin);
  if (isRunning && !wasRunning)
    initialPosition();

  wasRunning = isRunning;
}

// Lettura delle velocità di rotazione sul seriale
void readVelocities() {
  if (Serial.available()) {
    Serial.readBytes(serialBuffer, 2);
    signed char velocityX = (signed char) serialBuffer[0];
    signed char velocityY = (signed char) serialBuffer[1];
    periodMotorX = velocityToPeriod(velocityX, directionX);
    periodMotorY = velocityToPeriod(velocityY, directionY);
  }
}

// Converte il valore di velocità di rotazione in valore di periodo di incremento PWM
unsigned long velocityToPeriod(signed char velocity, int& dir) {
  if (velocity == 0) {
    return INF;
  } else {
    // Direzione = segno della velocità
    dir = velocity / abs(velocity);
    return 70535UL - abs(velocity) * 535UL;
  }
}

// Calcolo del successivo valore di PWM da settare su una singola fase
void nextPWM(int& value, int& sign, int dir) {
  
  // Incremento o riduzuzione del valore di PWM
  value += sign * dir;

  // Se il valore è sceso sotto lo 0, inversione del segno e PWM ricomincia a salire
  if (value < 0) {
    sign = -sign;
    value = -value;

  // Se il valore è salito sopra 255, inversione del segno e PWM ricomincia a scendere
  } else if (value > 255) {
    sign = -sign;
    value = 255 + (255 - value);
  }
}

// Settaggio dei valori di PWM calcolati sui pin
void writePWMs() {
  analogWrite(phaseX1, pwmX1);
  analogWrite(phaseX2, pwmX2);
  analogWrite(phaseX3, pwmX3);
  analogWrite(phaseY1, pwmY1);
  analogWrite(phaseY2, pwmY2);
  analogWrite(phaseY3, pwmY3);
}
