AS := nasm
LD := ld

%.o: %.asm
	$(AS) $(ASFLAGS) -o $@ $<

hello: ASFLAGS += -f elf
hello: LDFLAGS += -m elf_i386
hello: hello.o
	$(LD) $(LDFLAGS) -o $@ $<

.PHONY: all clean

all: hello

debug: ASFLAGS += -gdwarf
debug: all

clean:
	rm -rvf hello *.o

# nasm -MG hello.asm -o hello.o | tee -a Makefile
hello.o : hello.asm lib.asm

