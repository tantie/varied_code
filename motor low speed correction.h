// Пины для датчиков Холла
const int hallSensor1 = 2;
const int hallSensor2 = 3;

// Пины для управления двигателями
const int motor1PWM = 5;
const int motor2PWM = 6;

volatile int count1 = 0; // Счетчик оборотов для первого вала
volatile int count2 = 0; // Счетчик оборотов для второго вала

const int targetCount = 10; // Целевое количество оборотов для измерения

void setup() {
  pinMode(hallSensor1, INPUT);
  pinMode(hallSensor2, INPUT);
  pinMode(motor1PWM, OUTPUT);
  pinMode(motor2PWM, OUTPUT);
  
  attachInterrupt(digitalPinToInterrupt(hallSensor1), countRPM1, RISING);
  attachInterrupt(digitalPinToInterrupt(hallSensor2), countRPM2, RISING);
  
  Serial.begin(9600);
}

void loop() {
  if (count1 >= targetCount && count2 >= targetCount) {
    // Корректируем скорость двигателей
    adjustMotorSpeed(count1, count2);

    // Сбрасываем счетчики оборотов
    count1 = 0;
    count2 = 0;
  }
}

void countRPM1() {
  count1++;
}

void countRPM2() {
  count2++;
}

void adjustMotorSpeed(int rpm1, int rpm2) {
  int speedDifference = rpm1 - rpm2;

  // Устанавливаем базовую скорость для двигателей
  int baseSpeed = 128; // Примерное значение

  // Корректируем скорость двигателей
  analogWrite(motor1PWM, baseSpeed - speedDifference);
  analogWrite(motor2PWM, baseSpeed + speedDifference);

  // Выводим информацию на серийный порт
  Serial.print("Count1: ");
  Serial.print(rpm1);
  Serial.print(" Count2: ");
  Serial.print(rpm2);
  Serial.print(" Speed Difference: ");
  Serial.println(speedDifference);
}
