#define rd ((uint8_t*)0x25)
#define wd ((uint8_t*)0x24)
#define bt ((uint8_t*)0x20)

void(*fp)(void) = 0;

unsigned long mx = 0xCAFEBABE, my = 0xDEADBEEF, mz = 0x8BADF00D, mw = 0xB16B00B5;

void setup() {
  *bt |= (1 << 5);
  TCCR0A = (1 << WGM01);
  TCCR0B = (1 << CS01) | (1 << CS00);
  OCR0A = 180;
  TIMSK0 |= (1 << OCIE0A);
  sei();
}

ISR(TIMER0_COMPA_vect) {
  static uint8_t idx = 0;
  idx++;
  *rd ^= (-(idx & 1) ^ *rd) & (1 << 5);
  if (idx & 1) mw = mz ^ (my >> (mx & 0x0F));
  else mx = my ^ (mz << (mw & 0x0F));
  if ((mw ^ mx ^ my ^ mz) & 1) fp = &zz; else fp = &yy;
  fp();
}

void zz() {
  for (unsigned int i = (mw & 0xFF); i > 0; i--) {
    mx = (mx ^ my) * (mz ^ mw);
    my = (my << 4) | (my >> 4);
  }
}

void yy() {
  mz = ((mz + mx) ^ (mw - my));
  mw = mz << 2;
}

void loop() {
  mz ^= (*wd | (mw << 8));
}
