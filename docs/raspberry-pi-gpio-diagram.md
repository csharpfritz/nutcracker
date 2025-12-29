# Raspberry Pi GPIO Pin Diagram for WS2812B LED Strip

## Pin Layout (40-pin GPIO header)

```
     3V3  (1) (2)  5V
   GPIO2  (3) (4)  5V
   GPIO3  (5) (6)  GND
   GPIO4  (7) (8)  GPIO14
     GND  (9) (10) GPIO15
  GPIO17 (11) (12) GPIO18  ← **DATA PIN FOR LEDs**
  GPIO27 (13) (14) GND
  GPIO22 (15) (16) GPIO23
     3V3 (17) (18) GPIO24
  GPIO10 (19) (20) GND
   GPIO9 (21) (22) GPIO25
  GPIO11 (23) (24) GPIO8
     GND (25) (26) GPIO7
   GPIO0 (27) (28) GPIO1
   GPIO5 (29) (30) GND
   GPIO6 (31) (32) GPIO12
  GPIO13 (33) (34) GND
  GPIO19 (35) (36) GPIO16
  GPIO26 (37) (38) GPIO20
     GND (39) (40) GPIO21
```

## WS2812B LED Strip Connections

### Required Connections:
1. **VCC (Red wire)** → **Pin 2 (5V)** or **Pin 4 (5V)**
2. **GND (Black/White wire)** → **Pin 6 (GND)**, **Pin 9 (GND)**, **Pin 14 (GND)**, **Pin 20 (GND)**, **Pin 25 (GND)**, **Pin 30 (GND)**, **Pin 34 (GND)**, or **Pin 39 (GND)**
3. **DIN/Data (Green wire)** → **Pin 12 (GPIO18)**

### Physical Pin Layout Visual:
```
[3V3] [5V ]  ← Pin 1, 2
[GP2] [5V ]  ← Pin 3, 4
[GP3] [GND]  ← Pin 5, 6
[GP4] [G14]  ← Pin 7, 8
[GND] [G15]  ← Pin 9, 10
[G17] [G18]  ← Pin 11, 12 (GPIO18 = DATA)
[G27] [GND]  ← Pin 13, 14
[G22] [G23]  ← Pin 15, 16
[3V3] [G24]  ← Pin 17, 18
[G10] [GND]  ← Pin 19, 20
[GP9] [G25]  ← Pin 21, 22
[G11] [GP8]  ← Pin 23, 24
[GND] [GP7]  ← Pin 25, 26
```

## Troubleshooting Checklist:

### Power Issues:
- **LED strip not lighting at all**: Check 5V and GND connections
- **LEDs dim or flickering**: 5V power supply may be insufficient for your strip length
- **Only first few LEDs work**: Power supply can't handle full strip current draw

### Data Issues:
- **No response to commands**: Check GPIO18 (Pin 12) connection to DIN
- **Random colors/patterns**: Loose data connection or interference
- **Only first LED works**: Data signal not passing through strip properly

### Wire Colors (Common):
- **Red** = VCC (5V power)
- **Black/White** = GND (Ground)
- **Green/Yellow** = DIN (Data Input)

### Important Notes:
1. **GPIO18** is the **PWM-capable pin** - best for WS2812B timing
2. Use **Pin 12** (not pin 18 - that's GPIO24!)
3. Make sure connections are secure - breadboard jumpers can be loose
4. Test with a multimeter if possible:
   - 5V between VCC and GND
   - 3.3V between GPIO18 and GND when Pi is running

### Alternative Data Pins:
If GPIO18 doesn't work, you can try:
- **GPIO10** (Pin 19) - SPI MOSI
- **GPIO21** (Pin 40) - PCM
- **GPIO12** (Pin 32) - PWM

Update the code to use a different pin:
```python
pixels = neopixel.NeoPixel(board.D21, 256, brightness=0.1, auto_write=False)  # GPIO21
```

### Common Connection Mistakes:
1. Using **Pin 18** instead of **Pin 12** (Pin 18 is GPIO24, not GPIO18!)
2. Connecting to 3.3V instead of 5V (LEDs need 5V)
3. Loose ground connection
4. Reversed polarity on LED strip

### LED Strip Direction:
- Connect to the **input end** of the strip (usually has arrows showing data direction)
- Look for **DIN** (Data In) not **DOUT** (Data Out)