# Send and receive over UART

This guide shows you how to print text to your computer and echo what it sends back over the UART of a PIC16F877A with epic-hal, for a hobbyist who finished Getting started. A UART (universal asynchronous receiver/transmitter) is the serial port: two wires, one for each direction.

## Before you start

- You finished [Getting started](../getting-started/index.md), so epic-hal is cloned in `~/projects/epic-hal` and the epic-cc release is unpacked in `~/projects/epic-cc-release`.
- For the hardware steps, a PIC16F877A set up as in [Command line](../getting-started/cli.md) part 2, plus a USB serial adapter whose logic level matches your chip supply.

## Steps

1. Start the serial port at 115200 baud. The `lib/serial` HAL module keeps a ring buffer for each direction and runs on the USART interrupt, so your code never waits on the wire. `FOSC_HZ` is the clock speed, which the build provides.

    From `lib/serial/examples/example_serial.c` in epic-hal:

    ```c
    epic_serial_init(FOSC_HZ, 115200u);
    EPIC_IRQ_Restore(1);    /* arm the USART RX interrupt (init enables RCIE) */
    ```

    Initializing enables the receive interrupt, and `EPIC_IRQ_Restore(1)` sets the global interrupt enable so it can fire.

2. Send text one character at a time with `epic_serial_put_char`. The example keeps the text in a `const` array so the array lives in flash, not RAM.

    From `lib/serial/examples/example_serial.c` in epic-hal:

    ```c
    static const uint8_t banner[] = "epic-serial ready at 115200 8N1\r\n";
    for (uint8_t i = 0u; i < (uint8_t)(sizeof(banner) - 1u); i++)
    {
        epic_serial_put_char((char)banner[i]);
    }
    ```

    The module also has `epic_serial_put_u16`, `epic_serial_put_hex8` and others for numbers; see the [HAL module reference](../hal/index.md).

3. Receive by asking how many bytes are waiting, then reading them. The example sends every byte back, which is an echo.

    From `lib/serial/examples/example_serial.c` in epic-hal:

    ```c
    static uint8_t buf[8];
    for (;;)
    {
        if (epic_serial_available() > 0)
        {
            int n = epic_serial_read(buf, (int)sizeof(buf));
            if (n > 0)
            {
                epic_serial_write(buf, n);
            }
        }
    }
    ```

    `buf` is `static` on purpose: epic-cc does not yet support local arrays on a part without a hardware stack (see the [status page](../status.md)).

## Check that it works

Build the example from your epic-hal folder, using the flags from Getting started:

```bash
cd ~/projects/epic-hal
make epiccc-build MODULE=lib/serial MCU=16F877A EPIC_CC_HOST=1 \
  EPIC_CC_BIN=$(echo ~/projects/epic-cc-release/epic-cc-*/epic-cc)
```

The last line names the hex file:

```console
Built build/epiccc/16F877A-serial.hex
```

This build is a compile check. The simulator step in Getting started watches a pin, not serial output, and this guide has not run the example on a chip. To try it on hardware, flash the hex file, then cross the wires: chip pin RC6 (TX, pin 25) to the adapter's RX, chip pin RC7 (RX, pin 26) to the adapter's TX, and the grounds together. Open a terminal program at 115200 baud (for example `picocom -b 115200 /dev/ttyUSB0`). You should see the banner after reset, and every key you type comes back.

Warning: a 5 V adapter output can damage a chip that runs at 3.3 V, so match the adapter to the supply of the chip.

## On other families

`epic_serial_*` is the same on every family that lists `lib/serial` in the [HAL module reference](../hal/index.md). The pins used for TX and RX differ by part, so check yours in the [device matrix](../devices/index.md). Parts without a hardware UART need the `lib/swuart` module instead.

## Next

- [Timers and interrupts](timers-interrupts.md): the serial ring buffers run on the same interrupt machinery.
- [Drive and read pins](gpio.md).
