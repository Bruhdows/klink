/* ATtiny404-SSN. Pin/net assignments follow the native elevator netlist.
 * 20 MHz internal oscillator, no prescaler. UPDI remains enabled.
 */
#include "klink.h"
#include <avr/cpufunc.h>
#include <avr/interrupt.h>
#include <avr/io.h>
#include <avr/wdt.h>
#include <util/atomic.h>
static volatile uint32_t milliseconds;
ISR(TCB0_INT_vect) {
  milliseconds++;
  TCB0.INTFLAGS = TCB_CAPT_bm;
}
static uint32_t now_ms(void) {
  uint32_t n;
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE) { n = milliseconds; }
  return n;
}
static uint16_t adc(uint8_t channel) {
  ADC0.MUXPOS = channel;
  ADC0.INTFLAGS = ADC_RESRDY_bm;
  ADC0.COMMAND = ADC_STCONV_bm;
  uint32_t begin = now_ms();
  while (!(ADC0.INTFLAGS & ADC_RESRDY_bm))
    if ((uint32_t)(now_ms() - begin) > 3)
      return 0;
  return ADC0.RES;
}
static uint8_t crc8(const uint8_t *p, uint8_t n) {
  uint8_t c = 0;
  while (n--) {
    c ^= *p++;
    for (uint8_t i = 0; i < 8; i++)
      c = (c << 1) ^ ((c & 128) ? 7 : 0);
  }
  return c;
}
static void output(uint8_t duty) {
  TCA0.SINGLE.CMP2 = duty;
  if (duty)
    PORTA.OUTSET = PIN5_bm;
  else
    PORTA.OUTCLR = PIN5_bm;
}
int main(void) {
  PORTA.OUTCLR = PIN1_bm | PIN5_bm;
  PORTA.DIRSET = PIN1_bm | PIN5_bm; /* forward only */
  PORTB.OUTCLR = PIN2_bm;
  PORTB.DIRSET = PIN2_bm;
  _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, 0);
  _PROTECTED_WRITE(BOD.CTRLB, BOD_LVL_BODLEVEL2_gc);
  _PROTECTED_WRITE(BOD.CTRLA, BOD_ACTIVE_ENABLED_gc | BOD_SLEEP_ENABLED_gc);
  while (WDT.STATUS & WDT_SYNCBUSY_bm) {
  }
  _PROTECTED_WRITE(WDT.CTRLA, WDT_PERIOD_1KCLK_gc);
  ADC0.CTRLC = ADC_PRESC_DIV16_gc | ADC_REFSEL_VDDREF_gc;
  ADC0.SAMPCTRL = 16;
  ADC0.CTRLA = ADC_ENABLE_bm;
  PORTA.PIN6CTRL = PORT_ISC_INPUT_DISABLE_gc;
  PORTA.PIN7CTRL = PORT_ISC_INPUT_DISABLE_gc;
  TCA0.SINGLE.CTRLB = TCA_SINGLE_WGMODE_SINGLESLOPE_gc | TCA_SINGLE_CMP2EN_bm;
  TCA0.SINGLE.PER = 249;
  TCA0.SINGLE.CMP2 = 0;
  TCA0.SINGLE.CTRLA = TCA_SINGLE_CLKSEL_DIV16_gc | TCA_SINGLE_ENABLE_bm;
  TCB0.CCMP = 19999;
  TCB0.INTCTRL = TCB_CAPT_bm;
  TCB0.CTRLA = TCB_ENABLE_bm;
  TWI0.SADDR = 0x32 << 1;
  TWI0.SCTRLA = TWI_ENABLE_bm;
  sei();
  kl_lift lift;
  kl_lift_init(&lift);
  uint8_t rx[4], used = 0, txpos = 0, last_sequence = 0;
  bool overflow = false, have_sequence = false;
  uint32_t sampled = 0;
  uint16_t measured_vm = 0;
  for (;;) {
    uint32_t now = now_ms();
    uint8_t s = TWI0.SSTATUS;
    if (s & (TWI_BUSERR_bm | TWI_COLL_bm)) {
      used = 0;
      overflow = true;
      TWI0.SSTATUS = TWI_BUSERR_bm | TWI_COLL_bm;
      TWI0.SCTRLB = TWI_SCMD_COMPTRANS_gc;
    } else if (s & TWI_APIF_bm) {
      if (s & TWI_AP_bm) {
        used = 0;
        overflow = false;
        txpos = 0;
        TWI0.SCTRLB = TWI_SCMD_RESPONSE_gc;
      } else {
        /* Commit only on STOP: [command, duty, sequence, CRC8 polynomial 0x07].
         * 0=stop, 1=run/heartbeat, 2=clear. Clear never starts the motor.
         */
        if (!overflow && used == 4 && crc8(rx, 3) == rx[3]) {
          if (rx[0] == 0) {
            kl_lift_command(&lift, 0, now);
            output(0);
          } else if (rx[0] == 2 && !lift.running) {
            PORTA.OUTSET = PIN5_bm;
            uint32_t start = now_ms();
            while ((uint32_t)(now_ms() - start) < 2) {
            }
            if (kl_lift_clear(&lift, PORTA.IN & PIN4_bm, PORTA.IN & PIN2_bm,
                              measured_vm))
              have_sequence = false;
            output(0);
          } else if (rx[0] == 1 && rx[1] > 0 && rx[1] <= 180 && !lift.fault &&
                     (!have_sequence || (int8_t)(rx[2] - last_sequence) > 0)) {
            if (!lift.running) {
              PORTA.OUTSET = PIN5_bm;
              uint32_t start = now_ms();
              while ((uint32_t)(now_ms() - start) < 2) {
              }
            }
            if ((PORTA.IN & PIN4_bm) && (PORTA.IN & PIN2_bm)) {
              kl_lift_command(&lift, rx[1], now_ms());
              last_sequence = rx[2];
              have_sequence = true;
            } else {
              lift.fault |= KL_LIFT_STOP;
              output(0);
            }
          }
        }
        TWI0.SCTRLB = TWI_SCMD_COMPTRANS_gc;
      }
    } else if (s & TWI_DIF_bm) {
      if (s & TWI_DIR_bm) {
        TWI0.SDATA = txpos++ == 0 ? (uint8_t)lift.fault : lift.duty;
        TWI0.SCTRLB =
            (s & TWI_RXACK_bm) ? TWI_SCMD_COMPTRANS_gc : TWI_SCMD_RESPONSE_gc;
      } else {
        uint8_t b = TWI0.SDATA;
        if (used < 4)
          rx[used++] = b;
        else
          overflow = true;
        TWI0.SCTRLB = (overflow ? TWI_ACKACT_bm : 0) | TWI_SCMD_RESPONSE_gc;
      }
    }
    if ((uint32_t)(now - sampled) >= 5) {
      sampled = now;
      uint16_t current = (uint32_t)adc(6) * 3300u / 1023u * 1000u / 2870u;
      uint16_t vm = (uint32_t)adc(7) * 3300u * 172u / (1023ul * 22u);
      measured_vm = vm;
      uint8_t duty =
          kl_lift_step(&lift, now, !lift.running || (PORTA.IN & PIN4_bm),
                       !lift.running || (PORTA.IN & PIN2_bm),
                       PORTB.IN & PIN3_bm, current, vm);
      output(duty);
      wdt_reset();
    }
  }
}
