# Command line

In this tutorial you build the epic-hal 1 ms timebase example with epic-cc and `make`, watch it blink in the simulator, and then flash it to a PIC16F877A, for hobbyists who know some C but have not used a PIC microcontroller before. It takes about 30 minutes and needs no hardware for part 1; part 2 lists the parts.

A PIC is a small microcontroller chip, and the PIC16F877A is a common one. You need a Linux machine with `git`, `make`, `python3`, `unzip`, Docker that your user can run without `sudo`, and the GitHub CLI (`gh`) signed in with `gh auth login`.

## Part 1: in the simulator

1. Clone epic-hal and epic-cc side by side under `~/projects`. The simulator step expects that exact path.

    ```bash
    mkdir -p ~/projects && cd ~/projects
    git clone https://github.com/apojomovsky/epic-hal
    git clone https://github.com/apojomovsky/epic-cc
    ```

2. Download the epic-cc release. It carries its own pinned clang, so you install nothing else to compile. 

    ```bash
    mkdir -p ~/projects/epic-cc-release && cd ~/projects/epic-cc-release
    gh release download -R apojomovsky/epic-cc --pattern '*x86_64-linux.zip'
    unzip -q epic-cc-*-x86_64-linux.zip
    ```

3. Build the example. `lib/tick` is the HAL module that gives you a 1 ms timebase, and its example blinks an LED on pin RB0 every 500 ms. `EPIC_CC_BIN` names the downloaded compiler and `EPIC_CC_HOST=1` runs it directly on your machine; both are needed on every build.

    ```bash
    cd ~/projects/epic-hal
    make epiccc-build MODULE=lib/tick MCU=16F877A EPIC_CC_HOST=1 \
      EPIC_CC_BIN=$(echo ~/projects/epic-cc-release/epic-cc-*/epic-cc)
    ```

    More lines print first (the clock, the RAM use). The last lines show how much of the chip the program uses and where the hex file went:

    ```console
    epic-cc: program size for p16f877a:
      flash: 2544/8192 words (31.1%)
    Built build/epiccc/16F877A-tick.hex
    ```

    The source is `lib/tick/examples/example_tick.c` in epic-hal. The hex file is the program in a text format that programmers and the simulator read.

4. Build the image the simulator runs in. It is the epic-cc development image: the first run builds or pulls the clang compiler layer, which can take a long time, so start it and wait. Later runs skip it. Then link epic-cc into epic-hal, where the simulator target looks for it.

    ```bash
    make -C ~/projects/epic-cc image
    ln -sfn ~/projects/epic-cc ~/projects/epic-hal/epic-cc
    ```

5. Run the hex file in the simulator. The simulator models the processor but not the timer, so the command raises the timer interrupt itself (`IRQ_EVERY=200` steps, flag `PIR1:1`, enable `PIE1:1`) and watches bit 0 of `PORTB`, the register behind pin RB0. A step is one simulated instruction.

    ```bash
    make sim-epiccc HEX=build/epiccc/16F877A-tick.hex DEVICE=PIC16F877A \
      SAMPLES=12 STEPS=200000 IRQ_EVERY=200 IRQ_FLAG=PIR1:1 IRQ_ENABLE=PIE1:1
    ```

    The first run compiles the simulator, which takes under a minute. `/repo` in the output is the container's name for your epic-hal folder. The output ends with:

    ```console
    sample 11/12: PORTB:0=1
    sample 12/12: PORTB:0=0
    PASS: PORTB:0 toggled across 12 samples of 200000 steps (/repo/build/epiccc/16F877A-tick.hex, device PIC16F877A)
    ```

You now have a blinking pin, running in the simulator. The `PASS` line means RB0 changed value between samples, which is what an LED on that pin would show.

## Part 2: on a real chip

!!! warning
    Flashing is tested in the simulator and awaits sign-off on real chips; see [What's in 1.0](../status.md). The build writes the oscillator and watchdog settings for a 20 MHz crystal, so with a different crystal the chip will not run at the right speed.

You need a PIC16F877A, an XGecu T48 or TL866II Plus programmer, a breadboard, a 5 V supply, a 20 MHz crystal with two 22 pF capacitors, a 10 kilohm resistor, an LED, and a 330 ohm resistor.

1. Wire the chip. Pin numbers are for the 40-pin DIP package, counted from the notch end, pin 1 on the notch's left. Add a 0.1 uF capacitor between VDD and VSS close to the chip.

    | Pin | Name | Connect to |
    |---|---|---|
    | 11 and 32 | VDD | +5 V |
    | 12 and 31 | VSS | ground |
    | 1 | MCLR | +5 V through the 10 kilohm resistor |
    | 13 and 14 | OSC1 and OSC2 | the crystal, each side also to ground through a 22 pF capacitor |
    | 33 | RB0 | the 330 ohm resistor, then the LED anode; LED cathode to ground |

2. Install [minipro](https://gitlab.com/DavidGriffith/minipro) from your distribution or build it from its README (the PlatformIO tutorial downloads its own copy), plug in the programmer, and seat the chip in its socket. The [programmers page](../tools/programmers.md) covers the udev rules that give your user access to the USB device.

3. Write the hex file to the chip, then move the chip to the breadboard and power it from the 5 V supply, with its ground joined to the chip's VSS.

    ```bash
    cd ~/projects/epic-hal
    minipro -p PIC16F877A@DIP40 -w build/epiccc/16F877A-tick.hex
    ```

The LED toggles every 500 ms, so it is on for half a second and off for half a second.

## What you just did

You compiled a C program for a PIC with epic-cc, using the HAL's timebase module from epic-hal, and the build wrote the chip's configuration along with the code. The simulator ran the same hex file that the programmer writes, so a program that passes there has the right shape before any wire is involved. Programmers and the other ways to flash are on the [programmers page](../tools/programmers.md).

## Next

- Read the [guides](../guides/index.md) to use other HAL modules, such as serial, in the same build.
- Look up your own part in the [device matrix](../devices/index.md).
