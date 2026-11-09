#include "stm32f4xx.h"
#include <stdint.h>
extern uint32_t _stack, _data_load, _data, _edata, _bss, _ebss;
extern int main(void);
extern void SysTick_Handler(void);
void OTG_FS_IRQHandler(void);
void Reset_Handler(void);
static void trap(void) {
  for (;;) {
  }
}
__attribute__((section(".vectors"), used)) void (*const vectors[98])(void) = {
    [0] = (void (*)(void))&_stack,
    [1] = Reset_Handler,
    [2] = trap,
    [3] = trap,
    [4] = trap,
    [5] = trap,
    [6] = trap,
    [11] = trap,
    [12] = trap,
    [14] = trap,
    [15] = SysTick_Handler,
    [16 + OTG_FS_IRQn] = OTG_FS_IRQHandler};
void Reset_Handler(void) {
  uint32_t *s = &_data_load;
  for (uint32_t *d = &_data; d < &_edata;)
    *d++ = *s++;
  for (uint32_t *d = &_bss; d < &_ebss;)
    *d++ = 0;
  SCB->VTOR = (uint32_t)vectors;
  main();
  trap();
}
