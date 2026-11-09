#include "klink.h"
#include "stm32f4xx.h"
#include "tusb.h"
#include <string.h>
uint32_t SystemCoreClock = 168000000;
static volatile uint32_t ticks;
void SysTick_Handler(void) { ticks++; }
uint32_t tusb_time_millis_api(void) { return ticks; }
void OTG_FS_IRQHandler(void) { tusb_int_handler(0, true); }
static kl_node node;
static kl_vm vm;
static bool faulted, storage_ok, boot_arm;
static uint16_t control_status;
static bool control_valid;
static USART_TypeDef *const serial[] = {USART1, USART2, USART3,
                                        UART4,  UART5,  USART6};
static struct {
  uint8_t data[512];
  uint16_t head, tail;
} tx[6];
static struct {
  uint8_t uid[12];
  uint16_t address, neighbors[6];
  uint32_t seen;
} topology[64];
static unsigned count;
static struct {
  uint16_t target;
  uint8_t type, rails;
  bool active;
} leases[64];
static uint32_t heartbeat;
static uint8_t staging[KL_PROGRAM_SIZE], received[KL_PROGRAM_SIZE];
static kl_decoder usb_rx;
static void pin(GPIO_TypeDef *g, unsigned p, unsigned mode, unsigned af) {
  g->MODER = (g->MODER & ~(3u << (2 * p))) | (mode << (2 * p));
  g->AFR[p / 8] =
      (g->AFR[p / 8] & ~(15u << (4 * (p % 8)))) | (af << (4 * (p % 8)));
}
static void stop(void) {
  boot_arm = false;
  for (unsigned i = 0; i < 64; i++)
    leases[i].active = false;
  kl_vm_stop(&vm);
  kl_packet p = {.type = KL_STOP, .dst = KL_BROADCAST, .ttl = 64};
  kl_publish(&node, &p);
}
static void fail(void) {
  faulted = true;
  kl_vm_stop(&vm);
  GPIOC->BSRR = 1u << 13;
}
static void send(void *ctx, uint8_t port, const uint8_t *p, size_t n) {
  (void)ctx;
  if (port >= 6)
    return;
  unsigned free = (tx[port].tail - tx[port].head - 1) & 511;
  if (n > free) {
    fail();
    return;
  }
  while (n--) {
    tx[port].data[tx[port].head] = *p++;
    tx[port].head = (tx[port].head + 1) & 511;
  }
}
static void report(const kl_packet *p) {
  uint8_t data[KL_FRAME];
  size_t n = kl_encode(p, data);
  if (tud_cdc_connected() && tud_cdc_write_available() >= n)
    tud_cdc_write(data, n);
  if (tud_hid_ready()) {
    memset(data + n, 0, KL_FRAME - n);
    uint8_t report_data[64] = {0};
    memcpy(report_data, data, n);
    tud_hid_report(0, report_data, 64);
  }
}
static void deliver(void *ctx, const kl_packet *p) {
  (void)ctx;
  if (p->type == KL_FAULT) {
    faulted = true;
    stop();
    report(p);
    return;
  }
  if (p->type == KL_TOPOLOGY && p->len == 24) {
    unsigned i;
    for (i = 0; i < count; i++)
      if (!memcmp(topology[i].uid, p->data, 12))
        break;
    if (i == count) {
      if (count == 64) {
        fail();
        return;
      }
      memcpy(topology[i].uid, p->data, 12);
      uint16_t address = p->src < 2 || p->src == KL_BROADCAST ? 2 : p->src;
      bool used;
      do {
        used = false;
        for (unsigned j = 0; j < count; j++)
          if (topology[j].address == address) {
            address++;
            if (address == KL_BROADCAST)
              address = 2;
            used = true;
            break;
          }
      } while (used);
      topology[i].address = address;
      count++;
    }
    kl_packet assign = {
        .type = KL_ASSIGN, .dst = KL_BROADCAST, .ttl = 64, .len = 14};
    memcpy(assign.data, p->data, 12);
    assign.data[12] = topology[i].address;
    assign.data[13] = topology[i].address >> 8;
    kl_publish(&node, &assign);
    topology[i].seen = ticks;
    for (unsigned j = 0; j < 6; j++)
      topology[i].neighbors[j] =
          p->data[12 + 2 * j] | ((uint16_t)p->data[13 + 2 * j] << 8);
  }
  bool was_armed = vm.armed;
  if (!faulted)
    kl_vm_event(&vm, p, ticks);
  if (was_armed && !vm.armed) {
    stop();
    faulted = true;
  }
  report(p);
}
static bool wait_flag(volatile uint32_t *r, uint32_t mask, bool set,
                      uint32_t timeout) {
  uint32_t start = ticks;
  while (((*r & mask) != 0) != set)
    if (ticks - start > timeout)
      return false;
  return true;
}
static bool spi(uint8_t value, uint8_t *out) {
  if (!wait_flag(&SPI1->SR, SPI_SR_TXE, true, 2))
    return false;
  *(volatile uint8_t *)&SPI1->DR = value;
  if (!wait_flag(&SPI1->SR, SPI_SR_RXNE, true, 2))
    return false;
  *out = *(volatile uint8_t *)&SPI1->DR;
  return true;
}
static bool byte(uint8_t v) {
  uint8_t ignored;
  return spi(v, &ignored);
}
static void select(bool v) { GPIOA->BSRR = 1u << (v ? 31 : 15); }
static bool address(uint8_t cmd, uint32_t a) {
  return byte(cmd) && byte(a >> 16) && byte(a >> 8) && byte(a);
}
static bool ready(uint32_t timeout) {
  uint32_t start = ticks;
  do {
    uint8_t status;
    select(true);
    bool ok = byte(5) && spi(0xff, &status);
    select(false);
    if (!ok)
      return false;
    if (!(status & 1))
      return true;
    IWDG->KR = 0xaaaa;
  } while (ticks - start <= timeout);
  return false;
}
static bool flash_read(uint32_t at, uint8_t *d, unsigned n) {
  select(true);
  bool ok = address(3, at);
  while (ok && n--)
    ok = spi(0xff, d++);
  select(false);
  return ok;
}
static bool write_enable(void) {
  select(true);
  bool ok = byte(6);
  select(false);
  return ok;
}
static bool erase(uint32_t at) {
  if (!write_enable())
    return false;
  select(true);
  bool ok = address(0x20, at);
  select(false);
  return ok && ready(1000);
}
static bool page(uint32_t at, const uint8_t *d, unsigned n) {
  if (n > 256 - (at & 255) || !write_enable())
    return false;
  select(true);
  bool ok = address(2, at);
  while (ok && n--)
    ok = byte(*d++);
  select(false);
  return ok && ready(10);
}
#define RECORD KL_SAVED_SIZE
static uint32_t generation, slot = 4096;
static uint32_t u32(const uint8_t *p) {
  return p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) |
         ((uint32_t)p[3] << 24);
}
static void load(void) {
  uint8_t a[RECORD], b[RECORD];
  kl_saved pa, pb;
  bool va = flash_read(0, a, sizeof a) && kl_saved_decode(&pa, a),
       vb = flash_read(4096, b, sizeof b) && kl_saved_decode(&pb, b);
  kl_saved *s = 0;
  if (va && (!vb || (int32_t)(u32(a) - u32(b)) > 0)) {
    s = &pa;
    slot = 0;
  } else if (vb) {
    s = &pb;
    slot = 4096;
  }
  if (s) {
    vm.program = s->program;
    generation = s->generation;
    count = s->count;
    boot_arm = vm.program.count > 0;
    for (unsigned i = 0; i < count; i++) {
      memcpy(topology[i].uid, s->identities[i].uid, 12);
      topology[i].address = s->identities[i].address;
      leases[i].target = topology[i].address;
      leases[i].type = s->identities[i].module;
      leases[i].rails = s->identities[i].rails;
      leases[i].active = leases[i].rails != 0;
    }
  }
  /* Stored programs always need explicit ARM after boot. */
}
static bool save(void) {
  uint8_t d[RECORD], check[RECORD];
  kl_saved saved = {.generation = generation + 1, .count = count};
  if (!kl_program_decode(&saved.program, staging, sizeof staging))
    return false;
  for (unsigned i = 0; i < count; i++) {
    memcpy(saved.identities[i].uid, topology[i].uid, 12);
    saved.identities[i].address = topology[i].address;
    for (unsigned j = 0; j < 64; j++)
      if (leases[j].active && leases[j].target == topology[i].address) {
        saved.identities[i].module = leases[j].type;
        saved.identities[i].rails = leases[j].rails;
      }
  }
  if (!kl_saved_encode(&saved, d))
    return false;
  uint32_t next = slot ? 0 : 4096;
  if (!erase(next))
    return false;
  for (unsigned at = 0; at < RECORD - 1;) {
    unsigned n = RECORD - 1 - at;
    if (n > 256)
      n = 256;
    if (!page(next + at, d + at, n))
      return false;
    at += n;
  }
  if (!flash_read(next, check, RECORD - 1) || memcmp(d, check, RECORD - 1))
    return false;
  uint8_t commit = 0;
  if (!page(next + RECORD - 1, &commit, 1) ||
      !flash_read(next, check, RECORD) || !kl_saved_decode(&saved, check))
    return false;
  slot = next;
  generation = saved.generation;
  vm.program = saved.program;
  return true;
}
static void host(const kl_packet *p) {
  if (p->type == 32 && p->len == 0) {
    stop();
    memset(received, 0, sizeof received);
  } else if (p->type == 33 && p->len >= 3) {
    unsigned at = p->data[0] | ((unsigned)p->data[1] << 8), n = p->len - 2;
    if (at + n <= sizeof staging) {
      memcpy(staging + at, p->data + 2, n);
      memset(received + at, 1, n);
    }
  } else if (p->type == 34 && p->len == 0) {
    kl_vm_stop(&vm);
    bool full = true;
    for (unsigned i = 0; i < sizeof received; i++)
      if (!received[i])
        full = false;
    if (!full || !storage_ok || !save())
      fail();
  } else if (p->type == 35 && p->len == 1) {
    if (!p->data[0])
      stop();
    else if (!faulted && storage_ok && control_valid &&
             (control_status & (1u << 15)) && vm.program.count)
      vm.armed = true;
  } else if (p->type == 36 && p->len == 0) {
    for (unsigned i = 0; i < count; i++) {
      kl_packet o = {.type = KL_TOPOLOGY,
                     .src = topology[i].address,
                     .dst = 1,
                     .ttl = 1,
                     .len = 24};
      memcpy(o.data, topology[i].uid, 12);
      for (unsigned j = 0; j < 6; j++) {
        o.data[12 + j * 2] = topology[i].neighbors[j];
        o.data[13 + j * 2] = topology[i].neighbors[j] >> 8;
      }
      report(&o);
    }
  } else if (p->type == KL_STOP) {
    stop();
  } else if (!faulted &&
             (p->type == KL_RGB || p->type == KL_GATE || p->type == KL_POWER ||
              p->type == 10 || p->type == 11)) {
    if (p->type == KL_POWER && p->len == 2 && p->dst != KL_BROADCAST) {
      unsigned i;
      for (i = 0; i < 64; i++)
        if (leases[i].active && leases[i].target == p->dst)
          break;
      if (i == 64)
        for (i = 0; i < 64; i++)
          if (!leases[i].active)
            break;
      if (i == 64)
        return;
      leases[i].active = p->data[1] != 0;
      leases[i].target = p->dst;
      leases[i].type = p->data[0];
      leases[i].rails = p->data[1];
    }
    kl_packet out = *p;
    kl_publish(&node, &out);
  }
  kl_packet status = {.type = KL_FAULT,
                      .src = 1,
                      .dst = 1,
                      .ttl = 1,
                      .len = 2,
                      .seq = p->seq,
                      .data = {faulted, storage_ok}};
  report(&status);
}
static void delay_us(uint32_t us) {
  uint32_t at = DWT->CYCCNT;
  while ((uint32_t)(DWT->CYCCNT - at) < us * 168u) {
  }
}
static bool scl(bool high) {
  GPIOB->BSRR = 1u << (high ? 8 : 24);
  uint32_t start = ticks;
  while (high && !(GPIOB->IDR & (1u << 8)))
    if (ticks - start > 2)
      return false;
  delay_us(5);
  return true;
}
static void sda(bool high) {
  GPIOB->BSRR = 1u << (high ? 9 : 25);
  delay_us(5);
}
static void i2c_stop(void) {
  scl(false);
  sda(false);
  scl(true);
  sda(true);
}
static bool i2c_start(void) {
  sda(true);
  if (!scl(true) || !(GPIOB->IDR & (1u << 9)))
    return false;
  sda(false);
  return true;
}
static bool i2c_byte(uint8_t v) {
  for (unsigned i = 0; i < 8; i++) {
    scl(false);
    sda(v & 128);
    if (!scl(true))
      return false;
    v <<= 1;
  }
  scl(false);
  sda(true);
  if (!scl(true))
    return false;
  bool ack = !(GPIOB->IDR & (1u << 9));
  scl(false);
  return ack;
}
static bool i2c_inputs(uint8_t data[2]) {
  bool ok = i2c_start() && i2c_byte(0x40) && i2c_byte(0);
  if (ok)
    ok = i2c_start() && i2c_byte(0x41);
  for (unsigned j = 0; j < 2 && ok; j++) {
    uint8_t v = 0;
    sda(true);
    for (unsigned i = 0; i < 8; i++) {
      if (!scl(true)) {
        ok = false;
        break;
      }
      v = (v << 1) | ((GPIOB->IDR >> 9) & 1);
      scl(false);
    }
    data[j] = v;
    sda(j == 1);
    if (!scl(true))
      ok = false;
    scl(false);
  }
  i2c_stop();
  return ok;
}
uint16_t tud_hid_get_report_cb(uint8_t itf, uint8_t id, hid_report_type_t type,
                               uint8_t *data, uint16_t len) {
  (void)itf;
  (void)id;
  (void)type;
  (void)data;
  (void)len;
  return 0;
}
void tud_hid_set_report_cb(uint8_t itf, uint8_t id, hid_report_type_t type,
                           const uint8_t *data, uint16_t len) {
  (void)itf;
  (void)id;
  (void)type;
  static kl_decoder decoder;
  for (unsigned i = 0; i < len; i++) {
    kl_packet p;
    if (kl_feed(&decoder, data[i], &p))
      host(&p);
  }
}
int main(void) {
  /* Internal HSI runs until the external 8 MHz bypass oscillator is stable. */
  RCC->AHB1ENR |= 15;
  (void)RCC->AHB1ENR;
  GPIOC->BSRR = 1u << 13;
  pin(GPIOC, 13, 1, 0);
  GPIOB->BSRR = (1u << 14) << 16;
  pin(GPIOB, 14, 1, 0);
  pin(GPIOB, 15, 0, 0);
  GPIOB->PUPDR = (GPIOB->PUPDR & ~(3u << 30)) | (1u << 30);
  SysTick_Config(16000);
  RCC->APB1ENR |= RCC_APB1ENR_PWREN;
  PWR->CR |= PWR_CR_VOS;
  RCC->CR |= RCC_CR_HSEBYP | RCC_CR_HSEON;
  if (!wait_flag(&RCC->CR, RCC_CR_HSERDY, true, 100))
    for (;;) {
    }
  FLASH->ACR = FLASH_ACR_LATENCY_5WS | FLASH_ACR_ICEN | FLASH_ACR_DCEN |
               FLASH_ACR_PRFTEN;
  RCC->PLLCFGR = 8u | (336u << 6) | RCC_PLLCFGR_PLLSRC_HSE | (7u << 24);
  RCC->CFGR = RCC_CFGR_PPRE1_DIV4 | RCC_CFGR_PPRE2_DIV2;
  RCC->CR |= RCC_CR_PLLON;
  if (!wait_flag(&RCC->CR, RCC_CR_PLLRDY, true, 100))
    for (;;) {
    }
  RCC->CFGR |= RCC_CFGR_SW_PLL;
  if (!wait_flag(&RCC->CFGR, RCC_CFGR_SWS_1, true, 100))
    for (;;) {
    }
  SysTick_Config(168000);
  CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
  DWT->CYCCNT = 0;
  DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
  GPIOB->BSRR = (1u << 8) | (1u << 9);
  GPIOB->OTYPER |= (1u << 8) | (1u << 9);
  pin(GPIOB, 8, 1, 0);
  pin(GPIOB, 9, 1, 0);
  pin(GPIOB, 12, 0, 0);
  GPIOB->PUPDR = (GPIOB->PUPDR & ~(3u << 24)) | (1u << 24);
  RCC->APB1ENR |= RCC_APB1ENR_USART2EN | RCC_APB1ENR_USART3EN |
                  RCC_APB1ENR_UART4EN | RCC_APB1ENR_UART5EN;
  RCC->APB2ENR |=
      RCC_APB2ENR_USART1EN | RCC_APB2ENR_USART6EN | RCC_APB2ENR_SPI1EN;
  GPIO_TypeDef *const gp[] = {GPIOA, GPIOB, GPIOC, GPIOD};
  const uint8_t pins[][5] = {{1, 6, 1, 7, 7},   {0, 2, 0, 3, 7},
                             {1, 10, 1, 11, 7}, {0, 0, 0, 1, 8},
                             {2, 12, 3, 2, 8},  {2, 6, 2, 7, 8}};
  for (unsigned i = 0; i < 6; i++) {
    pin(gp[pins[i][0]], pins[i][1], 2, pins[i][4]);
    pin(gp[pins[i][2]], pins[i][3], 2, pins[i][4]);
    serial[i]->BRR = (i == 0 || i == 5 ? 84000000u : 42000000u) / 19200u;
    serial[i]->CR1 = USART_CR1_UE | USART_CR1_TE | USART_CR1_RE;
  }
  GPIOA->BSRR = 1u << 15;
  pin(GPIOA, 15, 1, 0);
  pin(GPIOA, 5, 2, 5);
  pin(GPIOA, 6, 2, 5);
  pin(GPIOA, 7, 2, 5);
  GPIOA->OSPEEDR |= (1u << 10) | (1u << 12) | (1u << 14);
  SPI1->CR1 =
      SPI_CR1_MSTR | SPI_CR1_SSM | SPI_CR1_SSI | SPI_CR1_BR_2 | SPI_CR1_SPE;
  pin(GPIOA, 11, 2, 10);
  pin(GPIOA, 12, 2, 10);
  GPIOA->OSPEEDR |= (3u << 22) | (3u << 24);
  RCC->AHB2ENR |= RCC_AHB2ENR_OTGFSEN;
  kl_node_init(&node, 1, 6, send, deliver, 0);
  memcpy(node.uid, (void *)UID_BASE, 12);
  IWDG->KR = 0x5555;
  IWDG->PR = 4;
  IWDG->RLR = 1000;
  IWDG->KR = 0xaaaa;
  IWDG->KR = 0xcccc;
  select(true);
  uint8_t id[3] = {0};
  storage_ok =
      byte(0x9f) && spi(0xff, id) && spi(0xff, id + 1) && spi(0xff, id + 2);
  select(false);
  storage_ok = storage_ok && id[0] == 0xef && id[1] == 0x40 && id[2] == 0x16;
  if (storage_ok)
    load();
  tusb_rhport_init_t init = {.role = TUSB_ROLE_DEVICE,
                             .speed = TUSB_SPEED_FULL};
  if (!tusb_init(0, &init))
    fail();
  if (GPIOB->IDR & (1u << 12))
    tud_disconnect();
  if (!faulted)
    GPIOC->BSRR = 1u << (13 + 16);
  uint32_t hello = 0;
  for (;;) {
    tud_task();
    static uint32_t control_poll;
    if (ticks - control_poll >= 100) {
      control_poll = ticks;
      uint8_t inputs[2];
      control_valid = i2c_inputs(inputs);
      if (control_valid) {
        control_status = inputs[0] | ((uint16_t)inputs[1] << 8);
        if ((control_status & (1u << 14)) || inputs[0] != 255) {
          stop();
          faulted = true;
        }
        kl_packet status = {.type = 12,
                            .src = 1,
                            .dst = 1,
                            .ttl = 1,
                            .len = 2,
                            .data = {inputs[0], inputs[1]}};
        if (!(GPIOB->IDR & (1u << 15)))
          report(&status);
      } else {
        stop();
        faulted = true;
      }
    }
    bool present = !(GPIOB->IDR & (1u << 12));
    static bool connected;
    if (present != connected) {
      connected = present;
      if (present)
        tud_connect();
      else
        tud_disconnect();
    }
    for (unsigned i = 0; i < 6; i++) {
      uint32_t status = serial[i]->SR;
      if (status & 15) {
        (void)serial[i]->DR;
        node.rx[i].discard = true;
        fail();
      } else if (status & USART_SR_RXNE)
        kl_receive(&node, i, (uint8_t)serial[i]->DR, ticks);
      if ((status & USART_SR_TXE) && tx[i].head != tx[i].tail) {
        serial[i]->DR = tx[i].data[tx[i].tail];
        tx[i].tail = (tx[i].tail + 1) & 511;
      }
    }
    uint8_t data[64];
    unsigned n = tud_cdc_read(data, sizeof data);
    for (unsigned i = 0; i < n; i++) {
      kl_packet p;
      if (kl_feed(&usb_rx, data[i], &p))
        host(&p);
    }
    tud_cdc_write_flush();
    if (ticks - hello >= 1000) {
      hello = ticks;
      kl_hello(&node, ticks);
      for (unsigned i = 0; i < count; i++)
        if (ticks - topology[i].seen > 6500 && vm.armed) {
          stop();
          faulted = true;
        }
    }
    if (!boot_arm && !faulted && ticks - heartbeat >= 200) {
      heartbeat = ticks;
      for (unsigned i = 0; i < 64; i++)
        if (leases[i].active) {
          bool present = false;
          for (unsigned j = 0; j < count; j++)
            if (topology[j].seen && topology[j].address == leases[i].target &&
                ticks - topology[j].seen < 6000)
              present = true;
          if (!present) {
            if (ticks > 7000) {
              stop();
              faulted = true;
            }
            continue;
          }
          kl_packet keep = {.type = KL_POWER,
                            .dst = leases[i].target,
                            .ttl = 64,
                            .len = 2,
                            .data = {leases[i].type, leases[i].rails}};
          kl_publish(&node, &keep);
        }
    }
    if (boot_arm && ticks > 5000 && !faulted && storage_ok && control_valid &&
        (control_status & (1u << 15))) {
      bool found = true;
      for (unsigned i = 0; i < vm.program.count; i++) {
        uint16_t ids[2] = {vm.program.rules[i].source,
                           vm.program.rules[i].target};
        for (unsigned k = 0; k < 2; k++)
          if (ids[k] != 1 && ids[k] != KL_BROADCAST) {
            bool alive = false;
            for (unsigned j = 0; j < count; j++)
              if (topology[j].seen && topology[j].address == ids[k] &&
                  ticks - topology[j].seen < 6000)
                alive = true;
            if (!alive)
              found = false;
          }
      }
      if (found) {
        vm.armed = true;
        boot_arm = false;
      }
    }
    kl_vm_tick(&vm, &node, ticks);
    IWDG->KR = 0xaaaa;
  }
}
