ENTRY(render_hook)
SECTIONS {
 . = 0x000a0000;
 .text : { KEEP(*(.text*)) }
 .rodata : { KEEP(*(.rodata*)) }
 .data : { KEEP(*(.data*)) KEEP(*(.sdata*)) KEEP(*(.got*)) }
 .bss : { KEEP(*(.bss*)) KEEP(*(.sbss*)) *(COMMON) }
 /DISCARD/ : { *(.MIPS.abiflags) *(.reginfo) *(.pdr) *(.comment) *(.note*) *(.eh_frame*) }
}
