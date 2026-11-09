# Firmware

These are bring-up projects for the actual CH32X035G8U6 tile, STM32F405RGT6 Hub and ATtiny404-SSN elevator. They compile and have host tests. They have not run on assembled Klink hardware.

## Build

Install Make, a host C compiler, Clang with RISC-V and ARM backends, LLD, and AVR-GCC with ATtiny404 device support. An AVR-GCC installation without the device files needs the [Microchip ATtiny device pack](https://packs.download.microchip.com/). Extract it outside the repository and set `AVR_DFP` to its directory.

```sh
cd firmware
make test
make images AVR_DFP=/absolute/path/to/Microchip.ATtiny_DFP
```

`AVR_GCC` and `CLANG` can select compiler executables. `BUILD` selects the output directory. The tested compilers are Clang 23 and AVR-GCC 7.3.0 with Microchip ATtiny device support. A normal `make` builds all images and runs the host tests. No files are downloaded by the build.

The linker scripts enforce the tile's 62KiB flash and 20KiB RAM and the Hub's 1MiB flash and 128KiB ordinary SRAM. USB buffers do not use CCM. AVR-GCC uses the ATtiny404's device memory map. Build products stay in `build/`.

Program the tile through DIO/DCK, the Hub through SWD, and the elevator through UPDI. Keep UPDI enabled. Read the elevator oscillator fuse and select 20MHz before using this image. Do not program fuses blindly or power the boards through monitor/debug pins.

## Implemented behavior

The tile starts with module power and module signals disabled. It reads the resistor ID for 100ms before accepting a module, samples the bus and fault inputs, and requires a Hub address assignment before enabling a known module. Commands can switch the protected rails, set both RGB LEDs, drive the gate PWM, send I2C writes, and control the elevator. RGB uses SPI DMA at 24MHz with thirty encoded ticks per LED bit. Nominal V5 pulse widths are 333/917ns for zero and 625/625ns for one, followed by at least 1ms low reset; host tests inspect the encoded waveform. Scope the real clock and waveform before accepting these margins. New color commands coalesce while a frame is active. GPIO I2C uses PC16/PC17 and avoids the CH32 hardware-I2C silicon-lot restriction. The X035 has no ordinary GPIO open-drain mode: the implementation releases each line as a floating input and drives only low, following its register definitions. PC10/PC11 aliases stay floating and USB pin ownership stays disabled. Module power needs a fresh lease within 500ms. Faults latch until reset. The watchdog resets a stalled loop.

The Hub has six 19200-baud UART interfaces, a self-powered HID/CDC USB device, topology reports, UID-based address assignment and USB command routing. It stores a CRC-protected event program, UID/address bindings and admitted module rail policies in alternating 4KiB W25Q32 sectors. It writes and verifies a new record before programming its commit byte. It leaves the old sector intact. A valid stored program can arm after five seconds when its referenced nodes are present and the hardware reports ARMED. Hardware or communications faults stop automation; faults do not automatically clear. GPIO I2C reads the TCA9535 input registers without changing its input configuration. The external USB_PRESENT_N signal controls USB attachment; unplugging USB does not stop a standalone program.

The event engine has sixteen rules. A rule matches a tile and input event, then schedules an RGB, gate or stop action. Each rule has one pending slot. A second event before that action executes stops the program rather than silently losing an action. Modules admitted during upload are renewed by the Hub every 200ms. Admission is a commissioning decision, not a measured power budget. Automatic topology-based wattage allocation is not implemented.

The elevator uses a default-off driver, forward PWM up to 180/249, 5ms current/voltage sampling, normally closed stop, driver fault input and index transitions. A command must be refreshed within 500ms. Missing progress for 1500ms, abnormal supply, excessive measured current, stop opening or driver fault latches shutdown. Clear never starts the motor. Reverse travel is deliberately unavailable in this bring-up image because the chain's anti-rollback mechanism is unqualified.

## Protocol

UART is 19200 baud, 8N1. A zero delimiter terminates a COBS frame. The decoded bytes are version 1, type, TTL, payload length, source address, destination address, sequence, payload and CRC16-CCITT-FALSE. The three integers are little-endian 16-bit values. Payloads have at most 48 bytes. Encoded frames have at most 62 bytes including the delimiter. CRC covers all decoded bytes before the CRC.

Address 1 is the Hub; 65535 is broadcast. HELLO is link-local and carries the twelve-byte hardware UID. It expires after three seconds. Topology packets carry that UID and six neighbor-address slots; tiles use four slots. The Hub assigns collision-free short addresses to UIDs and saves the bindings with the program. Short addresses before assignment are provisional. HELLO runs each second; topology runs every two seconds with a per-tile startup phase offset.

Flooding excludes the ingress port and decrements TTL. A per-source 32-packet replay window covers 64 tiles plus the Hub. Topology identities have separate UID-qualified windows so equal provisional addresses can be discovered. The cache expires after four seconds to admit rebooted senders; a reboot can therefore have a discovery delay. TTL still bounds a delayed packet's circulation. No cryptographic authentication is provided.

Commands are RGB=2, event=3, gate=4, stop=5, fault=6, power=7, topology=8, assignment=9, elevator=10, I2C-write=11 and hardware-status=12. USB upload commands are begin=32, chunk=33, commit=34, arm=35 and topology query=36. An upload chunk starts with its little-endian byte offset. A Hub acknowledgement echoes the request sequence; it confirms Hub handling, not physical actuator motion.

The HID interface uses fixed 64-byte input/output reports with a COBS frame followed by zero padding. CDC carries the same framed stream. The VID/PID are private bench identifiers from the TinyUSB example range. Assign suitable identifiers before distributing devices.

The elevator's I2C address is 0x32. Its four-byte write is command, duty, sequence and CRC8 polynomial 0x07, initial zero. Commands are stop=0, run/heartbeat=1 and clear=2. A run accepts only a fresh sequence. Reads return fault flags followed by current duty. Keep the motor stopped while changing programs or rail admission.

## USB commissioning client

`tools/klink.py` uses Python's standard library on POSIX systems. It does not install a desktop application.

```sh
python3 tools/klink.py --port /dev/ttyACM0 discover
python3 tools/klink.py --port /dev/ttyACM0 rgb 1234 ff2000
python3 tools/klink.py --port /dev/ttyACM0 power 1234 servo 1
python3 tools/klink.py --port /dev/ttyACM0 gate 1234 1
python3 tools/klink.py --port /dev/ttyACM0 stop
```

Use addresses returned by discovery. An upload JSON contains `rules` and optional `modules`. Each module has `address`, `type` (`button`, `sensor`, `servo` or `elevator`) and `rails` (1=5V, 2=20V, 3=both). Each rule has `source`, `target`, `event`, `action` (`rgb`, `gate` or `stop`), optional `delay_ms`, and `data`. RGB needs three bytes; gate needs one byte, 0 or 1; stop has no data. Input events are 1 on activation and 0 on release.

Upload with `upload file.json`, then use `arm`. The admitted policies are part of the saved record. Inspect the measured power budget before admitting any actuator. Unknown IDs, ID changes and faults disable the tile outputs. `lift ADDRESS clear` never starts a motor. `lift ADDRESS run --duty 100 --duration 3` sends fresh commands for a bounded supervised test and stops afterward. Do not use it before mechanical and stop tests.

## Bring-up dependencies

The STUSB4500 must first be programmed and read back through PD_SERVICE as specified in [Rev A](../docs/specifications/rev-a.md). The factory PDO2 can be 15V, which the Hub correctly rejects. This firmware does not replace that manufacturing operation or validate the PD NVM. The USB data port does not power the Hub.

Test UART overruns and ring-buffer load on real grids, UID reads, address collisions, clock accuracy, RGB timing, ADC calibration, USB enumeration/unplug, I2C stretching/NACK, flash interruption, watchdog recovery, module removal and motor faults. Firmware cannot qualify contact current, missing-ground faults, converter layout, protection transients or motor braking energy. See the [prototype plan](../docs/specifications/prototype-plan.md).

## Third-party sources

The register headers and USB stack are vendored so a clean checkout builds offline once toolchains are installed. Their licenses remain beside the code.

- WCH CH32X035 EVT: `openwch/ch32x035`, commit `af1c85f9dada11d71ceaa8866b8874399567e97e`. Its headers are licensed for WCH microcontrollers.
- TinyUSB: `hathach/tinyusb`, commit `9ca0a7491f35e8cf55cb8fcecb37bd87961c874f`, MIT.
- STM32F4 CMSIS device: `STMicroelectronics/cmsis-device-f4`, commit `9192c7b9df75a142f2027ab266601fe061fc00b3`, BSD-3-Clause.
- CMSIS core: `ARM-software/CMSIS_6`, commit `3c860f7a5810a34205bdbadb84b6d5f78f1cb322`, Apache-2.0.
