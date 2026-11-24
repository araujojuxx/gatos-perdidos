# Requer devkitARM (devkitPro). Rode "make" para gerar gatosperdidos.gba
PREFIX := arm-none-eabi-
TARGET := gatosperdidos

all: $(TARGET).gba

# so use "make gfx" se voce editar gen_gfx.py (precisa de Python 3 + Pillow opcional)
gfx:
	python3 gen_gfx.py

$(TARGET).elf: main.c gfx.h
	$(PREFIX)gcc -mthumb -mthumb-interwork -O2 -Wall -specs=gba.specs main.c -o $@

$(TARGET).gba: $(TARGET).elf
	$(PREFIX)objcopy -O binary $< $@
	gbafix $@ -tGATOSPERDIDO

clean:
	rm -f $(TARGET).elf $(TARGET).gba

.PHONY: all gfx clean
