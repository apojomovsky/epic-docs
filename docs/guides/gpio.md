# Drive and read pins

This guide shows you how to set a pin as an output, drive it, and read a button on a PIC16F877A with epic-hal, for a hobbyist who finished Getting started. Other families of the hardware abstraction layer (HAL) use the same calls; see [on other families](#on-other-families).

## Before you start

- You finished [Getting started](../getting-started/index.md), so epic-hal is cloned in `~/projects/epic-hal` and the epic-cc release is unpacked in `~/projects/epic-cc-release`.
- For the hardware steps, the wiring from [Command line](../getting-started/cli.md) part 2: a PIC16F877A with a 20 MHz crystal and an LED with a 330 ohm resistor on RB0.

## Steps

1. Set the pin direction once, at startup. `GPIOB` is port B, `GPIO_PIN_0` is RB0, and `GPIO_MODE_OUTPUT` makes the pin drive its level. You can combine several pins with `|` in one call.

    From `lib/tick/examples/example_tick.c` in epic-hal:

    ```c
    EPIC_GPIO_Init(GPIOB, GPIO_PIN_0, GPIO_MODE_OUTPUT);
    ```

2. Drive the pin high or low with `EPIC_GPIO_WritePin`. This turns the LED on, then off, around a 500 ms delay (the [timers guide](timers-interrupts.md) explains the delay):

    From `lib/tick/examples/example_tick.c` in epic-hal:

    ```c
    EPIC_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_SET);
    epic_tick_delay_ms(BLINK_MS);
    EPIC_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_RESET);
    ```

3. Flip a pin without knowing its level with `EPIC_GPIO_TogglePin`. From `lib/tick/examples/example_tick.c` in epic-hal, in the loop that blinks the LED:

    ```c
    EPIC_GPIO_TogglePin(GPIOB, GPIO_PIN_0);
    ```

4. Read an input. Set the direction to `GPIO_MODE_INPUT`, then compare `EPIC_GPIO_ReadPin` with `GPIO_PIN_SET`. This is from `lib/debounce/examples/example_debounce.c`, where buttons on RB0 and RB1 go to VCC with 10 kilohm pull-down resistors, so a pressed button reads high:

    ```c
    EPIC_GPIO_Init(GPIOB, GPIO_PIN_0 | GPIO_PIN_1, GPIO_MODE_INPUT);
    EPIC_GPIO_Init(GPIOB, GPIO_PIN_2 | GPIO_PIN_3, GPIO_MODE_OUTPUT);
    ```

    From `lib/debounce/examples/example_debounce.c`, the read function both buttons share:

    ```c
    static bool read_button(void *ctx)
    {
        button_pin_t *b = (button_pin_t *)ctx;
        return EPIC_GPIO_ReadPin(b->port, b->pin) == GPIO_PIN_SET;
    }
    ```

    Here `button_pin_t` holds a port and a pin, so one function serves both buttons.

    A mechanical button bounces for a few milliseconds when pressed. The example hands the read to the `lib/debounce` HAL module, which commits a level only after it holds for 20 ms. Read a raw button directly only when a bounce does not matter.

## Check that it works

Build the output example from your epic-hal folder. This is the command from Getting started, with the module named after the file above:

```bash
cd ~/projects/epic-hal
make epiccc-build MODULE=lib/tick MCU=16F877A EPIC_CC_HOST=1 \
  EPIC_CC_BIN=$(echo ~/projects/epic-cc-release/epic-cc-*/epic-cc)
```

The last line names the hex file:

```console
Built build/epiccc/16F877A-tick.hex
```

Run it in the simulator, which watches bit 0 of `PORTB`, the register behind RB0:

```bash
make sim-epiccc HEX=build/epiccc/16F877A-tick.hex DEVICE=PIC16F877A \
  SAMPLES=12 STEPS=200000 IRQ_EVERY=200 IRQ_FLAG=PIR1:1 IRQ_ENABLE=PIE1:1
```

The output ends with a line that starts `PASS: PORTB:0 toggled across 12 samples of 200000 steps`. On hardware, flash the hex file as in Getting started and the LED lights for half a second, then blinks.

The input example builds with `MODULE=lib/debounce` and writes `build/epiccc/16F877A-debounce-sizecheck.hex`. It is a compile check: the simulator step here cannot press a button, and this guide has not run it on a chip.

## On other families

`EPIC_GPIO_*` and the `GPIOB` and `GPIO_PIN_n` names are the same on every family, and `lib/tick` and `lib/debounce` build for any family that lists them. Pin numbers, which ports exist and the register behind each port differ by part, so check your part in the [device matrix](../devices/index.md) and the [HAL module reference](../hal/index.md).

## Next

- [Timers and interrupts](timers-interrupts.md): run code on a schedule instead of waiting in a loop.
- [Send and receive over UART](uart.md): print to your computer.
