CFLAGS += -ansi -Wall -Werror -pedantic -nostdlib -fno-builtin
# for MAP_ANONYMOUS
CFLAGS += -D_GNU_SOURCE
LD := ld
AS := nasm
ASFLAGS += -f elf64

C_SOURCES := $(wildcard *.c)
ASM_SOURCES := $(filter-out sys-syscall.asm, $(wildcard *.asm))
SOURCES := $(C_SOURCES) $(ASM_SOURCES)
OBJECTS := $(C_SOURCES:%.c=%.o) $(ASM_SOURCES:%.asm=%.o)

%.o: %.asm
	$(AS) $(ASFLAGS) -o $@ $<

printf: $(OBJECTS)
	$(LD) $(LDFLAGS) -o $@ $^

sys-syscall.asm: /usr/include/asm/unistd_64.h
	grep "^#define __NR_"  $< \
		| sed -e "s/__NR/SYS/" -e "s/^#/%/" \
		> $@

.PHONY: all release debug objects clean deps

all: printf

release: CFLAGS += -O3
release: all
	strip printf

debug: CFLAGS += -g -Og
debug: ASFLAGS += -gdwarf
debug: all

objects: $(OBJECTS)

clean:
	rm -rfv vgcore.* *.o *.plist \
		printf sys-syscall.asm

deps:
	touch sys-syscall.asm
	nasm -MG syscall.asm -o syscall.o | tee -a Makefile
	rm sys-syscall.asm
	gcc -MM *.c | tee -a Makefile

syscall.o : syscall.asm sys-syscall.asm

alloc.o: alloc.c alloc.h syscall.h printf.h
list.o: list.c list.h alloc.h
main.o: main.c syscall.h printf.h alloc.h list.h
printf.o: printf.c printf.h syscall.h
