/* CH32X035G8U6; all four UARTs remap 0. Polling bring-up image.
 * No interrupt can delay RGB waveforms. Hardware protection remains
 * independent.
 */
#include "klink.h"
#include "vendor/ch32x035.h"
#define CLOCK 48000000u
static kl_node node;
static USART_TypeDef *const uart[] = {USART1, USART2, USART3, USART4};
static uint32_t ms, last_count;
static uint32_t now(void) {
  uint32_t v = (uint32_t)SysTick->CNT;
  ms += (v - last_count) / 48000u;
  last_count += ((v - last_count) / 48000u) * 48000u;
  return ms;
}
static void wait_us(uint32_t us) {
  uint32_t t = (uint32_t)SysTick->CNT;
  while ((uint32_t)((uint32_t)SysTick->CNT - t) < us * 48u) {
  }
}
static void mode(GPIO_TypeDef *g, unsigned pin, unsigned value) {
  volatile uint32_t *r = pin < 8 ? &g->CFGLR : pin < 16 ? &g->CFGHR : &g->CFGXR;
  unsigned shift = (pin % 8) * 4;
  *r = (*r & ~(15u << shift)) | (value << shift);
}
static void low(GPIO_TypeDef *g, unsigned pin) { g->BCR = 1u << pin; }
static void high(GPIO_TypeDef *g, unsigned pin) {
  if (pin < 16)
    g->BSHR = 1u << pin;
  else
    g->BSXR = 1u << (pin - 16);
}
static bool read(GPIO_TypeDef *g, unsigned pin) {
  return (g->INDR & (1u << pin)) != 0;
}
static uint32_t faults;
static uint8_t module, identified;
static uint32_t candidate_since, command_ms;
static bool powered;
static kl_debounce input;
static void off(void) {
  low(GPIOB, 6);
  low(GPIOB, 7);
  low(GPIOC, 0);
  powered = false;
  mode(GPIOB, 12, 4);
}
/* Nonblocking TX rings prevent a slow/disconnected neighbor from stalling
 * safety. */
static struct {
  uint8_t data[256];
  uint8_t head, tail;
} tx[4];
static void send(void *ctx, uint8_t port, const uint8_t *p, size_t n) {
  (void)ctx;
  if (port >= 4)
    return;
  unsigned free = (uint8_t)(tx[port].tail - tx[port].head - 1);
  if (n > free) {
    faults |= 2;
    off();
    return;
  }
  while (n--) {
    tx[port].data[tx[port].head++] = *p++;
  }
}
static uint16_t adc(unsigned channel) {
  ADC1->RSQR3 = channel;
  ADC1->STATR = 0;
  ADC1->CTLR2 |= ADC_SWSTART;
  uint32_t t = now();
  while (!(ADC1->STATR & 2))
    if (now() - t > 3) {
      faults |= 4;
      return 0;
    }
  return ADC1->RDATAR & 4095;
}
/* DMA keeps the 24MHz SPI stream continuous without blocking four UARTs. */
static uint8_t rgb_wire[KL_RGB_BYTES], rgb_pending[3];
static bool rgb_active, rgb_queued;
static uint32_t rgb_started, rgb_reset;
static void rgb(const uint8_t *p) {
  for (unsigned i = 0; i < 3; i++)
    rgb_pending[i] = p[i];
  rgb_queued = true;
}
static void rgb_service(void) {
  uint32_t t = now();
  if (rgb_active) {
    if ((DMA1->INTFR & DMA_TEIF3) || t - rgb_started > 3) {
      DMA1_Channel3->CFGR = 0;
      SPI1->CTLR2 = 0;
      rgb_active = false;
      faults |= 8;
      off();
      return;
    }
    if (!DMA1_Channel3->CNTR && !(SPI1->STATR & 128)) {
      DMA1_Channel3->CFGR = 0;
      SPI1->CTLR2 = 0;
      rgb_active = false;
      rgb_reset = t;
    }
  }
  if (!rgb_active && rgb_queued && t - rgb_reset >= 1) {
    kl_rgb_encode(rgb_pending, rgb_wire);
    rgb_queued = false;
    DMA1_Channel3->CFGR = 0;
    DMA1->INTFCR = DMA_CGIF3;
    DMA1_Channel3->PADDR = (uint32_t)&SPI1->DATAR;
    DMA1_Channel3->MADDR = (uint32_t)rgb_wire;
    DMA1_Channel3->CNTR = KL_RGB_BYTES;
    DMA1_Channel3->CFGR = DMA_CFGR3_DIR | DMA_CFGR3_MINC | DMA_CFGR3_PL_1;
    SPI1->CTLR2 = SPI_CTLR2_TXDMAEN;
    DMA1_Channel3->CFGR |= DMA_CFGR3_EN;
    rgb_started = t;
    rgb_active = true;
  }
}
static bool safe(void) {
  return read(GPIOB, 9) && read(GPIOA, 5) && read(GPIOC, 3) && !faults;
}
/* The X035 has no GPIO open-drain output mode. Release means floating input;
 * assert means a low output latch followed by push-pull output mode. RM 7.4.1.
 * The PC10/PC11 aliases remain floating and USB pin ownership stays disabled.
 */
static void i2c_line(unsigned pin, bool release) {
  if (release)
    mode(GPIOC, pin, 4);
  else {
    low(GPIOC, pin);
    mode(GPIOC, pin, 3);
  }
}
static bool scl(bool release) {
  i2c_line(16, release);
  uint32_t start = now();
  while (release && !read(GPIOC, 16))
    if (now() - start > 2)
      return false;
  wait_us(5);
  return true;
}
static void sda(bool release) {
  i2c_line(17, release);
  wait_us(5);
}
static void i2c_stop(void) {
  scl(false);
  sda(false);
  scl(true);
  sda(true);
}
static bool i2c_byte(uint8_t value) {
  for (unsigned i = 0; i < 8; i++) {
    if (!scl(false))
      return false;
    sda(value & 128);
    if (!scl(true))
      return false;
    value <<= 1;
  }
  scl(false);
  sda(true);
  if (!scl(true))
    return false;
  bool ack = !read(GPIOC, 17);
  scl(false);
  return ack;
}
static bool i2c_write(uint8_t address, const uint8_t *data, unsigned n) {
  high(GPIOB, 6);
  mode(GPIOC, 16, 4);
  mode(GPIOC, 17, 4);
  sda(true);
  if (!scl(true) || !read(GPIOC, 17)) {
    i2c_stop();
    return false;
  }
  sda(false);
  bool ok = i2c_byte(address << 1);
  for (unsigned i = 0; i < n && ok; i++)
    ok = i2c_byte(data[i]);
  i2c_stop();
  return ok;
}
static uint8_t lift_sequence;
static uint8_t lift_crc(const uint8_t *p) {
  uint8_t c = 0;
  for (unsigned i = 0; i < 3; i++) {
    c ^= p[i];
    for (unsigned j = 0; j < 8; j++)
      c = (c << 1) ^ ((c & 128) ? 7 : 0);
  }
  return c;
}
static void deliver(void *ctx, const kl_packet *p) {
  (void)ctx;
  if (p->type == KL_STOP) {
    off();
    return;
  }
  if (p->type == KL_RGB && p->len == 3) {
    rgb(p->data);
    return;
  }
  /* Explicit power command: module type + rail mask. No automatic load
   * admission. */
  if (p->type == KL_POWER && p->len == 2 && p->data[0] == module && module &&
      node.assigned && safe()) {
    uint8_t rails = p->data[1];
    if (rails & ~3u)
      return;
    if ((rails & 2) && module != KL_ELEVATOR)
      return;
    if (rails & 1)
      high(GPIOB, 7);
    else
      low(GPIOB, 7);
    if (rails & 2)
      high(GPIOC, 0);
    else
      low(GPIOC, 0);
    powered = rails != 0;
    command_ms = now();
    return;
  }
  if (p->type == 10 && p->len == 2 && module == KL_ELEVATOR && powered &&
      safe()) {
    uint8_t bytes[4] = {p->data[0], p->data[1], ++lift_sequence, 0};
    bytes[3] = lift_crc(bytes);
    if (!i2c_write(0x32, bytes, 4)) {
      faults |= 32;
      off();
    } else
      command_ms = now();
    return;
  }
  if (p->type == 11 && p->len >= 2 && p->data[0] < 128 && powered && safe()) {
    if (!i2c_write(p->data[0], p->data + 1, p->len - 1)) {
      faults |= 32;
      off();
    } else
      command_ms = now();
    return;
  }
  if (p->type == KL_GATE && p->len == 1 && module == KL_SERVO && powered &&
      safe()) {
    /* 50 Hz TIM1 CH4; 1 ms closed / 2 ms open, qualification required. */
    if (p->data[0] > 1)
      return;
    high(GPIOB, 6);
    mode(GPIOB, 12, 11);
    TIM1->CH4CVR = p->data[0] ? 2000 : 1000;
    command_ms = now();
  }
}
int main(void) {
  FLASH->ACTLR = (FLASH->ACTLR & ~FLASH_ACTLR_LATENCY) | FLASH_ACTLR_LATENCY_2;
  RCC->CFGR0 &= ~0xf0u;
  RCC->AHBPCENR |= RCC_DMA1EN;
  RCC->APB2PCENR |= RCC_AFIOEN | RCC_IOPAEN | RCC_IOPBEN | RCC_IOPCEN |
                    RCC_USART1EN | RCC_ADC1EN | RCC_SPI1EN | RCC_TIM1EN;
  AFIO->CTLR &= ~AFIO_CTLR_USB_IOEN;
  RCC->APB1PCENR |= RCC_USART2EN | RCC_USART3EN | RCC_USART4EN;
  /* Set output latches before taking pins out of reset/input state. */
  low(GPIOB, 6);
  low(GPIOB, 7);
  high(GPIOB, 8);
  low(GPIOC, 0);
  mode(GPIOB, 6, 3);
  mode(GPIOB, 7, 3);
  mode(GPIOB, 8, 3);
  mode(GPIOC, 0, 3);
  mode(GPIOA, 0, 0);
  mode(GPIOA, 6, 0);
  mode(GPIOA, 5, 8);
  high(GPIOA, 5);
  mode(GPIOC, 3, 8);
  high(GPIOC, 3);
  mode(GPIOB, 9, 8);
  high(GPIOB, 9);
  SysTick->CTLR = 0;
  SysTick->CNT = 0;
  SysTick->CMP = ~(uint64_t)0;
  SysTick->CTLR = 5;
  /* ADC /8, long sample period, software start. */
  ADC1->CTLR3 = 7;
  ADC1->SAMPTR2 = (7u << 0) | (7u << 18);
  ADC1->CTLR2 = ADC_ADON | ADC_EXTSEL | ADC_EXTTRIG;
  wait_us(50);
  const unsigned pins[][4] = {
      {1, 10, 1, 11}, {0, 2, 0, 3}, {1, 3, 1, 4}, {1, 0, 1, 1}};
  GPIO_TypeDef *const gp[] = {GPIOA, GPIOB};
  for (unsigned i = 0; i < 4; i++) {
    mode(gp[pins[i][0]], pins[i][1], 11);
    mode(gp[pins[i][2]], pins[i][3], 4);
    uart[i]->BRR = (CLOCK + 19200 / 2) / 19200;
    uart[i]->CTLR1 = (1u << 13) | (1u << 3) | (1u << 2);
  }
  mode(GPIOA, 7, 11);
  SPI1->CTLR1 = (1u << 2) | (0u << 3) | (1u << 8) | (1u << 9) | (1u << 14) |
                (1u << 15) | (1u << 6);
  AFIO->PCFR1 =
      (AFIO->PCFR1 & ~AFIO_PCFR1_TIM1_REMAP) | AFIO_PCFR1_TIM1_REMAP_1;
  TIM1->PSC = 47;
  TIM1->ATRLR = 19999;
  TIM1->CH4CVR = 1000;
  TIM1->CHCTLR2 = 6u << 12;
  TIM1->CCER = 1u << 12;
  TIM1->BDTR = 1u << 15;
  TIM1->CTLR1 = 1;
  /* WCH unique ID registers: retained in HELLO; short ID hash is provisional.
   */
  const uint8_t *uid = (const uint8_t *)0x1ffff7e8;
  bool all_zero = true, all_erased = true;
  for (unsigned i = 0; i < 8; i++) {
    if (uid[i])
      all_zero = false;
    if (uid[i] != 255)
      all_erased = false;
  }
  if (all_zero || all_erased)
    faults |= 128;
  uint16_t id = kl_crc(uid, 12);
  if (id < 2 || id == KL_BROADCAST)
    id = 2;
  kl_node_init(&node, id, 4, send, deliver, 0);
  for (unsigned i = 0; i < 12; i++)
    node.uid[i] = uid[i];
  low(GPIOB, 8);
  IWDG->CTLR = 0x5555;
  IWDG->PSCR = 4;
  IWDG->RLDR = 625;
  IWDG->CTLR = 0xaaaa;
  IWDG->CTLR = 0xcccc;
  uint32_t hello = 1000 + id % 1000, topo = 2000 + id % 2000, sample = 0;
  uint32_t fault_sent = 0, reported_faults = 0;
  uint8_t black[3] = {0};
  rgb(black);
  for (;;) {
    uint32_t t = now();
    for (unsigned i = 0; i < 4; i++) {
      uint16_t status = uart[i]->STATR;
      if (status & 15) {
        (void)uart[i]->DATAR;
        node.rx[i].discard = true;
        faults |= 16;
        off();
      } else if (status & 32)
        kl_receive(&node, i, (uint8_t)uart[i]->DATAR, t);
      if ((status & 128) && tx[i].head != tx[i].tail)
        uart[i]->DATAR = tx[i].data[tx[i].tail++];
    }
    rgb_service();
    if ((int32_t)(t - hello) >= 0) {
      hello = t + 1000;
      kl_hello(&node, t);
    }
    if ((int32_t)(t - topo) >= 0) {
      topo = t + 2000;
      kl_topology(&node);
    }
    if (t - sample >= 10) {
      sample = t;
      uint8_t candidate = kl_module(adc(6));
      if (candidate != identified) {
        identified = candidate;
        candidate_since = t;
        off();
        module = KL_NONE;
      }
      if (t - candidate_since >= 100)
        module = candidate;
      uint16_t bus = adc(0);
      if (bus < 1163 || bus > 1784) {
        off();
        if (t > 500)
          faults |= 64;
      }
      if (!read(GPIOB, 9) || !read(GPIOA, 5) || !read(GPIOC, 3))
        faults |= 1;
      if (!safe() || (powered && t - command_ms > 500)) {
        off();
      }
      if (powered && (module == KL_BUTTON || module == KL_SENSOR)) {
        /* Wait for external MODULE_5V_GOOD qualification before requesting I/O.
         */
        high(GPIOB, 6);
        mode(GPIOB, 12, 8);
        high(GPIOB, 12);
        if (kl_debounce_step(&input, !read(GPIOB, 12), t, 20)) {
          kl_packet event = {.type = KL_EVENT,
                             .dst = KL_BROADCAST,
                             .len = 1,
                             .data = {input.stable}};
          kl_publish(&node, &event);
        }
      }
      if (faults && (faults != reported_faults || t - fault_sent >= 1000)) {
        fault_sent = t;
        reported_faults = faults;
        kl_packet fault = {.type = KL_FAULT,
                           .dst = KL_BROADCAST,
                           .len = 1,
                           .data = {(uint8_t)faults}};
        kl_publish(&node, &fault);
      }
      IWDG->CTLR = 0xaaaa;
    }
  }
}
