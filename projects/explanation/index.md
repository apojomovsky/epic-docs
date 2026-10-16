# Explanation

These pages explain how epic8 works under the hood, for a hobbyist who finished [Getting started](../getting-started/index.md) and wants to know why the pieces fit the way they do. They give background, not steps: follow the tutorials and guides to build things.

- [How the toolchain fits together](toolchain.md): what epic-cc, epic-hal, epic-platformio, and epic-tools each own, and which path to pick.
- [How the HAL is structured](hal-structure.md): families, ports, modules, and the contract that keeps the same code building under two compilers.
- [What the simulator proves](simulator.md): the two simulators, what a passing run means, and what only a chip can show.
- [How a C file becomes a hex file](c-to-hex.md): the stages inside one `epic-cc` invocation, and the trade-offs they force.
