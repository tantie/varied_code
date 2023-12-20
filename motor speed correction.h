//arduino speed motor correction

// Пины для датчиков 
const int hallSensor1 = 2;
const int hallSensor2 = 3;

// Пины для управления двигателями
const int motor1PWM = 5;
const int motor2PWM = 6;

volatile int count1 = 0; // Счетчик оборотов для первого вала
volatile int count2 = 0; // Счетчик оборотов для второго вала

void setup() {
  // Начальная настройка
  pinMode(hallSensor1, INPUT);
  pinMode(hallSensor2, INPUT);
  pinMode(motor1PWM, OUTPUT);
  pinMode(motor2PWM, OUTPUT);
  
  attachInterrupt(digitalPinToInterrupt(hallSensor1), countRPM1, RISING);
  attachInterrupt(digitalPinToInterrupt(hallSensor2), countRPM2, RISING);
  
  Serial.begin(9600);
}

void loop() {
  // Считываем и сбрасываем счетчики оборотов
  int rpm1 = count1;
  int rpm2 = count2;
  count1 = 0;
  count2 = 0;

  // Рассчитываем и применяем корректировку скорости
  adjustMotorSpeed(rpm1, rpm2);

  // Ждем для следующего измерения
  delay(100);
}

void countRPM1() {
  count1++;
}

void countRPM2() {
  count2++;
}

void adjustMotorSpeed(int rpm1, int rpm2) {
  // Вычисляем разницу в скорости
  int speedDifference = rpm1 - rpm2;

  // Устанавливаем базовую скорость для двигателей
  int baseSpeed = 128; // Примерное значение, нужно подобрать

  // Корректируем скорость двигателей
  analogWrite(motor1PWM, baseSpeed - speedDifference);
  analogWrite(motor2PWM, baseSpeed + speedDifference);

  // Выводим информацию на серийный порт
  Serial.print("RPM1: ");
  Serial.print(rpm1);
  Serial.print(" RPM2: ");
  Serial.print(rpm2);
  Serial.print(" Speed Difference: ");
  Serial.println(speedDifference);
}
