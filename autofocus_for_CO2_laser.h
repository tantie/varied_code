#include <Servo.h>
#include <Wire.h>
#include <VL6180X.h>

#define SCALING 3 // Valid scaling factors are 1, 2, or 3.
VL6180X sensor;

int angle = 90; // начальное значение угла сервопривода
int mini = 28;
int centre = 30;
int maxi = 38;
int mm;
Servo myservo;

// Усреднение значений
#define AVERAGE_READINGS 5
int getAverageReading() {
    long sum = 0;
    for (int i = 0; i < AVERAGE_READINGS; i++) {
        sum += sensor.readRangeSingleMillimeters();
        delay(10);
    }
    return (int)(sum / AVERAGE_READINGS);
}

// Экспоненциальное скользящее среднее
float exponentialMovingAverage(float currentReading, float previousEMA, float alpha) {
    return alpha * currentReading + (1 - alpha) * previousEMA;
}

// Фильтр Калмана
float kalmanFilter(float currentReading, float &estimation, float &errEstimate, float processNoise, float measurementNoise) {
    float kalmanGain = errEstimate / (errEstimate + measurementNoise);
    estimation = estimation + kalmanGain * (currentReading - estimation);
    errEstimate = (1.0 - kalmanGain) * errEstimate + fabs(estimation - currentReading) * processNoise;
    return estimation;
}

// Глобальные переменные для фильтра Калмана и ЭСС
float estimation = 30.0;
float errEstimate = 1.0;
const float processNoise = 1.0;
const float measurementNoise = 10.0;
float previousEMA = 30.0;
const float alpha = 0.1;

void setup() {
  Serial.begin(9600);
  Wire.begin();

  myservo.attach(9);  // сервопривод на выводе 9
  myservo.write(angle);
  delay(10000); // пауза перед стартом работы
  Serial.print("start\n");

  sensor.init();
  sensor.configureDefault();
  sensor.setScaling(SCALING);

  sensor.writeReg(VL6180X::SYSRANGE__MAX_CONVERGENCE_TIME, 30);
  sensor.setTimeout(500);
}

void loop() {
  int mmRaw = sensor.readRangeSingleMillimeters();

  // метод фильтрации
  mm = getAverageReading(); // Усреднение
  // mm = (int)exponentialMovingAverage(mmRaw, previousEMA, alpha); // ЭСС
  // mm = (int)kalmanFilter(mmRaw, estimation, errEstimate, processNoise, measurementNoise); // Калман

  if (mm > centre) {
    while (mm < centre) {
      angle++;
      myservo.write(angle);
    }
  }

  if (mm < centre) {
    while (mm < centre) {
      angle--;
      myservo.write(angle);
    }
  }

  if (mm == centre) {
    delay(500);
  }

  delay(100);
}
