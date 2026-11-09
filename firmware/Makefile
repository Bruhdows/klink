BUILD ?= build
CC = cc
CLANG ?= clang
AVR_GCC ?= avr-gcc
AVR_DFP ?=
COMMON = -std=c11 -Os -Wall -Wextra -Werror -Wno-misleading-indentation -ffunction-sections -fdata-sections -Icommon
.PHONY: all clean
all: images test
$(BUILD):
	mkdir -p $@
$(BUILD)/klink.o: common/klink.c common/klink.h | $(BUILD)
	$(CC) $(COMMON) -c $< -o $@
$(BUILD)/libklink.a: $(BUILD)/klink.o
	ar rcs $@ $<
$(BUILD)/elevator.elf: elevator/main.c common/klink.c common/klink.h | $(BUILD)
	$(AVR_GCC) $(COMMON) -mmcu=attiny404 -DF_CPU=20000000UL $(if $(AVR_DFP),-B$(AVR_DFP)/gcc/dev/attiny404/ -I$(AVR_DFP)/include) -Wl,--gc-sections elevator/main.c common/klink.c -o $@
clean:
	rm -rf $(BUILD)

RISCV = --target=riscv32-unknown-elf -march=rv32imac -mabi=ilp32 -msmall-data-limit=0 -mno-relax
BARE = $(COMMON) -ffreestanding -fno-builtin -nostdlib -fuse-ld=lld -Wl,--gc-sections
$(BUILD)/tile.elf: tile/main.c tile/start.S tile/link.ld common/klink.c common/klink.h common/memory.c | $(BUILD)
	$(CLANG) $(RISCV) $(BARE) -std=gnu11 -Itile/vendor -Wl,-T,tile/link.ld,-Map,$(BUILD)/tile.map tile/start.S tile/main.c common/klink.c common/memory.c -o $@

ARM = --target=arm-none-eabi -mcpu=cortex-m4 -mthumb -mfloat-abi=soft
USB = hub/vendor/tinyusb
USB_SOURCES = $(USB)/tusb.c $(USB)/common/tusb_fifo.c $(USB)/device/usbd.c $(USB)/class/cdc/cdc_device.c $(USB)/class/hid/hid_device.c $(USB)/portable/synopsys/dwc2/dcd_dwc2.c $(USB)/portable/synopsys/dwc2/dwc2_common.c
$(BUILD)/hub.elf: hub/main.c hub/start.c hub/usb.c hub/tusb_config.h hub/link.ld common/klink.c common/klink.h common/memory.c $(USB_SOURCES) | $(BUILD)
	$(CLANG) $(ARM) $(BARE) -Wno-error=unused-parameter -Icommon/include -Ihub -I$(USB) -Ihub/vendor/stm32 -Ihub/vendor/cmsis -DSTM32F405xx -Wl,-T,hub/link.ld,-Map,$(BUILD)/hub.map hub/start.c hub/main.c hub/usb.c common/klink.c common/memory.c $(USB_SOURCES) -o $@

.PHONY: test images
images: $(BUILD)/tile.elf $(BUILD)/hub.elf $(BUILD)/elevator.elf
test: $(BUILD)/test_klink
	./$(BUILD)/test_klink
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_client.py' -v
$(BUILD)/test_klink: tests/test_klink.c common/klink.c common/klink.h | $(BUILD)
	$(CC) $(COMMON) -g -fsanitize=address,undefined tests/test_klink.c common/klink.c -o $@
