ENTRY(_start)
MEMORY { FLASH(rx) : ORIGIN = 0, LENGTH = 62K
         RAM(rwx) : ORIGIN = 0x20000000, LENGTH = 20K }
SECTIONS {
 .text : { KEEP(*(.init)) *(.text*) *(.rodata*) . = ALIGN(4); } > FLASH
 .data : { _data = .; *(.data*) *(.sdata*) . = ALIGN(4); _edata = .; } > RAM AT> FLASH
 _data_load = LOADADDR(.data);
 .bss (NOLOAD) : { _bss = .; *(.bss*) *(.sbss*) *(COMMON) . = ALIGN(4); _ebss = .; } > RAM
 _stack = ORIGIN(RAM) + LENGTH(RAM);
 ASSERT(_ebss + 2048 < _stack, "tile RAM overflow")
}
