ENTRY(Reset_Handler)
MEMORY { FLASH(rx) : ORIGIN = 0x08000000, LENGTH = 1024K
         RAM(rwx) : ORIGIN = 0x20000000, LENGTH = 128K }
SECTIONS {
 .text : { KEEP(*(.vectors)) *(.text*) *(.rodata*) . = ALIGN(4); } > FLASH
 .ARM.exidx : { *(.ARM.exidx*) } > FLASH
 .data : { _data = .; *(.data*) . = ALIGN(4); _edata = .; } > RAM AT> FLASH
 _data_load = LOADADDR(.data);
 .bss (NOLOAD) : { _bss = .; *(.bss*) *(COMMON) . = ALIGN(4); _ebss = .; } > RAM
 _stack = ORIGIN(RAM) + LENGTH(RAM);
 ASSERT(_ebss + 4096 < _stack, "Hub RAM overflow")
}
