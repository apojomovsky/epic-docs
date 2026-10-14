# PlatformIO

In this tutorial you build a blinking LED with the epic8 PlatformIO platform, watch it blink in the simulator, and then flash it to a PIC16F877A, for hobbyists who know some C but have not used a PIC microcontroller before. It takes about 30 minutes and needs no hardware for part 1; part 2 lists the parts.

You need a Linux machine with PlatformIO Core ([install guide](https://docs.platformio.org/en/latest/core/installation/)), plus `git`, `make`, `python3` and Docker that your user can run without `sudo`. The simulator step uses the last two.

## Part 1: in the simulator

1. Install the epic8 platform. Always write the owner, `apojomovsky/epic8`. This also fetches the compiler. Lines starting `Error:` or `Max retries` mean a download mirror is down and the next one is tried; the install worked if it ends with `has been installed`.

    ```bash
    pio pkg install -g --platform apojomovsky/epic8
    ```

2. Make a project folder and save this as `~/blink/platformio.ini`. The board is the PIC16F877A, `framework = epichal` brings in the hardware abstraction layer (HAL), and `-DEPIC_HAL_MODULES=tick` adds its 1 ms timebase module.

    ```bash
    mkdir -p ~/blink/src && cd ~/blink
    ```

    ```ini
    [env:epic8]
    platform = apojomovsky/epic8
    board = pic16f877a
    framework = epichal
    build_flags = -DEPIC_HAL_MODULES=tick
    ```

3. Save this program as `src/main.c`. It makes pin RB0 an output and toggles it every 500 ms. `EPIC_CONFIG` sets the chip's configuration words: a high-speed crystal at 4 MHz, with the watchdog and low-voltage programming off.

    ```c
    #include <stdint.h>

    #include <epic-cc.h>
    #include "epic_tick.h"
    #include "peripherals/hal_gpio.h"

    /* The oscillator and the watchdog are named here: left unset, the chip keeps
     * its erased fuses, which on the PIC16F877A are RC with the watchdog on. */
    EPIC_CONFIG("osc=hs, xtal_hz=4000000, wdt=off, lvp=off");

    #define FOSC_HZ EPIC_FOSC_HZ

    #define BLINK_MS 500u

    void main(void)
    {
        EPIC_GPIO_Init(GPIOB, GPIO_PIN_0, GPIO_MODE_OUTPUT);
        epic_tick_init(FOSC_HZ);

        for (;;) {
            EPIC_GPIO_TogglePin(GPIOB, GPIO_PIN_0);
            epic_tick_delay_ms(BLINK_MS);
        }
    }
    ```

    The source is `examples/hal-tick-pic16f877a` in epic-platformio.

4. Build it.

    ```bash
    pio run
    ```

    The build ends with a size report and `[SUCCESS]`. The hex file, the program in a text format that programmers and the simulator read, is `.pio/build/epic8/firmware.hex`.

5. Get the simulator. It lives in epic-hal and epic-cc, which must sit side by side under `~/projects`. If you already did the command line tutorial, skip the two `git clone` lines. The first image build can take a long time; later runs skip it.

    ```bash
    mkdir -p ~/projects && cd ~/projects
    git clone https://github.com/apojomovsky/epic-hal
    git clone https://github.com/apojomovsky/epic-cc
    make -C epic-cc image
    ln -sfn ~/projects/epic-cc ~/projects/epic-hal/epic-cc
    ```

6. Run your hex file in it. The simulator models the processor but not the timer, so the command raises the timer interrupt itself (`IRQ_EVERY=200` steps, flag `PIR1:1`, enable `PIE1:1`) and watches bit 0 of `PORTB`, the register behind pin RB0. A step is one simulated instruction. `/repo` in the output is the container's name for your epic-hal folder.

    ```bash
    cd ~/projects/epic-hal
    mkdir -p build && cp ~/blink/.pio/build/epic8/firmware.hex build/blink.hex
    make sim-epiccc HEX=build/blink.hex DEVICE=PIC16F877A \
      SAMPLES=12 STEPS=200000 IRQ_EVERY=200 IRQ_FLAG=PIR1:1 IRQ_ENABLE=PIE1:1
    ```

    The first run compiles the simulator, which takes a minute. The output ends with:

    ```console
    sample 12/12: PORTB:0=0
    PASS: PORTB:0 toggled across 12 samples of 200000 steps (/repo/build/blink.hex, device PIC16F877A)
    ```

You now have a blinking pin, running in the simulator. The `PASS` line means RB0 changed value between samples, which is what an LED on that pin would show.

## Part 2: on a real chip

!!! warning
    Flashing is tested in the simulator and awaits sign-off on real chips; see [What's in 1.0](../status.md). `EPIC_CONFIG` must match your hardware: with a different crystal the chip will not run at the right speed.

You need a PIC16F877A, an XGecu T48 or TL866II Plus programmer, a breadboard, a 5 V supply, a 4 MHz crystal with two 22 pF capacitors, a 10 kilohm resistor, an LED, and a 330 ohm resistor.

1. Wire the chip. Pin numbers are for the 40-pin DIP package, counted from the notch end, pin 1 on the notch's left. Add a 0.1 uF capacitor between VDD and VSS close to the chip.

    | Pin | Name | Connect to |
    |---|---|---|
    | 11 and 32 | VDD | +5 V |
    | 12 and 31 | VSS | ground |
    | 1 | MCLR | +5 V through the 10 kilohm resistor |
    | 13 and 14 | OSC1 and OSC2 | the crystal, each side also to ground through a 22 pF capacitor |
    | 33 | RB0 | the 330 ohm resistor, then the LED anode; LED cathode to ground |

2. Install the udev rules that give your user access to the programmer, and plug it in. Your user must be in the `plugdev` group (`sudo usermod -aG plugdev $USER`, then log out and in). The file only grants access to the USB programmer.

    ```bash
    curl -fsSLO https://raw.githubusercontent.com/apojomovsky/epic-platformio/master/udev/99-epic8.rules
    sudo cp 99-epic8.rules /etc/udev/rules.d/
    sudo udevadm trigger
    ```

3. Name the programmer in `platformio.ini`, which makes PlatformIO download its software. Add this line to the `[env:epic8]` section, seat the chip in the programmer's socket, and upload.

    ```ini
    upload_protocol = minipro
    ```

    ```bash
    cd ~/blink
    pio run -t upload
    ```

4. Move the chip to the breadboard and power it from the 5 V supply, with its ground joined to VSS.

The LED toggles every 500 ms, so it is on for half a second and off for half a second.

## What you just did

You asked PlatformIO to compile a C program for a PIC with epic-cc and the HAL's timebase module, and it wrote the chip's configuration along with the code. The simulator ran the same hex file that the programmer writes, so a program that passes there has the right shape before any wire is involved. Programmers and boards are on the [PlatformIO pages](../platformio/index.md) and the [programmers page](../tools/programmers.md).

## Next

- Read the [guides](../guides/index.md) to use other HAL modules, such as serial, in the same project.
- Look up your own part in the [boards list](../platformio/boards.md).
