# Timers and interrupts

This guide shows you how to wait without blocking, and how to run a function on a timer interrupt, on a PIC16F877A with epic-hal, for a hobbyist who finished Getting started.

## Before you start

- You finished [Getting started](../getting-started/index.md), so epic-hal is cloned in `~/projects/epic-hal` and the epic-cc release is unpacked in `~/projects/epic-cc-release`.
- You know how to [drive a pin](gpio.md).

## Steps

1. Start the 1 ms timebase once. `epic_tick_init` takes the clock speed, which the build provides as `FOSC_HZ`, and it also enables interrupts globally. The `lib/tick` hardware abstraction layer (HAL) module counts milliseconds on Timer2 for you.

    From `lib/tick/examples/example_tick.c` in epic-hal:

    ```c
    epic_tick_init(FOSC_HZ);        /* starts the 1 ms tick and enables GIE */
    ```

2. Wait with `epic_tick_delay_ms` when nothing else needs to run. It blocks, so the chip does nothing else meanwhile.

    From `lib/tick/examples/example_tick.c` in epic-hal:

    ```c
    epic_tick_delay_ms(BLINK_MS);
    ```

3. Keep the chip free instead by comparing timestamps. Read the time with `epic_tick_get`, and ask later how long has passed. The unsigned subtraction stays correct when the counter wraps around.

    From `lib/tick/examples/example_tick.c` in epic-hal:

    ```c
    uint32_t last = epic_tick_get();
    for (;;)
    {
        if (epic_tick_elapsed_since(last) >= BLINK_MS)
        {
            last = epic_tick_get();
            EPIC_GPIO_TogglePin(GPIOB, GPIO_PIN_0);
        }
    }
    ```

4. To react the moment a timer overflows, give the timer a callback. An interrupt pauses `main`, runs your function, then resumes `main`, so keep the function short and make anything it shares with `main` `volatile`. This is from `hal/pic14/16f87xa/tests/example_blink.c`:

    ```c
    static volatile uint32_t g_toggle_count = 0;

    static void on_t0_overflow(void)
    {
        EPIC_GPIO_TogglePin(GPIOB, GPIO_PIN_0);
        g_toggle_count++;
    }
    ```

5. Configure Timer0 with a handle, start it, and enable interrupts. The clock source is the instruction clock (a quarter of the crystal), divided by 256 here, so Timer0 overflows about every 13 ms at 20 MHz.

    From `hal/pic14/16f87xa/tests/example_blink.c`, the same test as step 4:

    ```c
    TIMER0_HandleTypeDef h = TIMER0_HANDLE_DEFAULT;
    h.ClockSource       = TIMER0_CLOCK_INTERNAL;
    h.Prescaler         = TIMER0_PRESCALER_1_256;
    h.PrescalerAssigned = true;
    h.ReloadValue       = 0x00U;
    h.OverflowCallback  = on_t0_overflow;
    EPIC_TIMER0_Init(&h);
    EPIC_TIMER0_Start(&h);

    EPIC_IRQ_Restore(1);
    ```

    Initializing the timer enables its interrupt, but nothing fires until `EPIC_IRQ_Restore(1)` sets the global interrupt enable.

## Check that it works

Build both examples from your epic-hal folder (the compiler flags are the ones from Getting started):

```bash
cd ~/projects/epic-hal
B=$(echo ~/projects/epic-cc-release/epic-cc-*/epic-cc)
make epiccc-build MODULE=lib/tick MCU=16F877A EPIC_CC_HOST=1 EPIC_CC_BIN=$B
make epiccc-build MODULE=hal/pic14/16f87xa MCU=16F877A EPIC_CC_HOST=1 EPIC_CC_BIN=$B
```

They write `build/epiccc/16F877A-tick.hex` and `build/epiccc/16F877A-blink.hex`. The simulator does not model the timers, so each run raises the timer flag itself. For the Timer0 example, that is flag `INTCON:2` and enable `INTCON:5`:

```bash
make sim-epiccc HEX=build/epiccc/16F877A-blink.hex DEVICE=PIC16F877A \
  SAMPLES=12 STEPS=200000 IRQ_EVERY=65536 IRQ_FLAG=INTCON:2 IRQ_ENABLE=INTCON:5
```

The output ends with a line that starts `PASS: PORTB:0 toggled across 12 samples of 200000 steps`. For the `lib/tick` example, use the simulator command from the [GPIO guide](gpio.md). On a chip, the Timer0 LED toggles about 76 times a second, too fast to see as blinking, and the tick example toggles every 500 ms. This guide has not run either on a chip.

## On other families

The `epic_tick_*` calls are the same on every family that lists `lib/tick` in the [HAL module reference](../hal/index.md). The timer handle, the prescaler names and the interrupt flag bits belong to each family, so step 5 is specific to this one. Find your part's timers in the [device matrix](../devices/index.md).

## Next

- [Send and receive over UART](uart.md): interrupts also drive the serial ring buffers.
- [Drive and read pins](gpio.md): what the callbacks toggle.
