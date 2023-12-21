// Пины для датчиков Холла
const int hallSensor1 = 2;
const int hallSensor2 = 3;

// Пины для управления двигателями
const int motor1PWM = 5;
const int motor2PWM = 6;

volatile int count1 = 0; // Счетчик оборотов для первого вала
volatile int count2 = 0; // Счетчик оборотов для второго вала

const int targetCount = 10; // Целевое количество оборотов для измерения
const unsigned long timeout = 5000; // Таймаут для проверки вращения (в миллисекундах)

unsigned long lastTime1 = 0; // Время последнего оборота для первого двигателя
unsigned long lastTime2 = 0; // Время последнего оборота для второго двигателя

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
    adjustMotorSpeed(count1, count2);
    count1 = 0;
    count2 = 0;
  }
  checkForStall();
}

void countRPM1() {
  count1++;
  lastTime1 = millis();
}

void countRPM2() {
  count2++;
  lastTime2 = millis();
}

void adjustMotorSpeed(int rpm1, int rpm2) {
  int speedDifference = rpm1 - rpm2;
  int baseSpeed = 128; //базовая скорость для двигателей

  // Корректируем скорость двигателей
  analogWrite(motor1PWM, baseSpeed - speedDifference);
  analogWrite(motor2PWM, baseSpeed + speedDifference);

  // Выводим информацию
  Serial.print("Count1: ");
  Serial.print(rpm1);
  Serial.print(" Count2: ");
  Serial.print(rpm2);
  Serial.print(" Speed Difference: ");
  Serial.println(speedDifference);
}

void checkForStall() {
  unsigned long currentTime = millis();

  if ((currentTime - lastTime1 > timeout) || (currentTime - lastTime2 > timeout)) {
    // Если один из двигателей застрял или остановлен
    Serial.println("Stall detected! Stopping motors.");

    // Остановка двигателей
    analogWrite(motor1PWM, 0);
    analogWrite(motor2PWM, 0);

  }
}
