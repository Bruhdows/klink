.section .init,"ax"
.global _start
_start:
 .option push
 .option norelax
 la sp, _stack
 .option pop
 la t0, trap
 csrw mtvec, t0
 la t0, _data_load
 la t1, _data
 la t2, _edata
1: bgeu t1,t2,2f
 lw t3,0(t0)
 sw t3,0(t1)
 addi t0,t0,4
 addi t1,t1,4
 j 1b
2: la t1,_bss
 la t2,_ebss
3: bgeu t1,t2,4f
 sw zero,0(t1)
 addi t1,t1,4
 j 3b
4: call main
trap: j trap
