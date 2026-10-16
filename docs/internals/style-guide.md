# epic8 documentation style guide

The rules every page in the epic8 family follows: the four project
repositories (epic-cc, epic-hal, epic-platformio, epic-tools) and this hub.
Design: epic-tasks `docs/08-docs-overhaul.md`. The prose lint enforces the
rules marked **(lint)**; reviewers check the rest.

## Who we write for

A hobbyist who knows some C and has blinked an LED on an Arduino or similar,
but may never have used a PIC, a cross-compiler or a hardware abstraction
layer. Every page assumes exactly that, and links to deeper pages for anyone
who wants more. When a page needs more background, it links to it instead of
assuming it.

## The four kinds of page

Every page is exactly one of these. Pick the kind before you write.

| Kind | Answers | Shape | Lives in |
|---|---|---|---|
| Tutorial | "Teach me" | One path, numbered steps, a working result at the end, no choices | Getting started |
| How-to guide | "How do I ...?" | Goal, prerequisites, steps, result; assumes the tutorial | Guides |
| Reference | "What exactly is ...?" | Complete, dry, scannable, mostly generated | Reference, device and module pages |
| Explanation | "Why / how does it work?" | Prose, diagrams, trade-offs, no steps | Explanation |

Internal design history (ADRs, design notes, experiments) is not one of
these: it lives under Internals and user pages never link to it.

## Voice

- Second person ("you"), present tense, active voice.
- Plain words and short sentences. One idea per sentence; one topic per
  paragraph; paragraphs of three to five sentences.
- Say what something does before how it works.
- No hype and no superlatives ("blazing", "powerful", "simply", "just",
  "easy"). **(lint)** Show it working instead.
- No jokes that need context; no emoji in prose.
- When something is a limitation, say so plainly and link the status page.
- No audience clause in a tagline or opening sentence; say what the project
  does and what is distinctive about it. "Who we write for" guides how pages
  explain things, not what they claim.

## Positioning (all public text)

- Lead with **fully open source, MIT licensed**: an auditable path from C to
  hex, with the HAL and the platform under the same licence.
- Never pitch "no XC8 licence needed": XC8 is free today, so that is not a
  reason to switch. **(lint)**
- Never publish XC8 size or speed numbers, listings or Memory Summaries, and
  never compare against XC8 by number. They stay in the private
  epic-benchmarks repository. **(lint: XC8 next to a number)**
- "No Microchip download on the default path" is fine as a convenience line.

## Terminology **(lint)**

Use exactly these spellings; the lint rejects the variants.

| Write | Not |
|---|---|
| epic8 (the family) | Epic8, EPIC8, epic 8 |
| epic-cc, epic-hal, epic-platformio, epic-tools | EpicCC, epic_cc, Epic-HAL |
| PIC12 baseline, PIC14 (mid-range), PIC14E (enhanced mid-range), PIC18 | PIC16 core, midrange, enhanced-midrange |
| part (one chip, for example PIC16F877A) | device, when a single chip is meant |
| family (parts sharing a HAL port, for example 16F87xA) | series |
| HAL module (for example the UART module) | driver, library, when a HAL module is meant |
| board (a PlatformIO board definition) | target |
| simulator (MPLAB-SIM through mdb) | emulator |
| hex file | HEX, binary |

Spell a part number exactly as Microchip does (PIC16F877A, PIC18F4550).
Expand an abbreviation the first time a page uses it.

## Structure

- One H1 per page, matching the navigation title.
- Headings in sentence case. **(lint)**
- The first sentence of every page says what the page is for and who it is
  for.
- Use lists for steps and parallel items, tables for comparisons, prose for
  reasoning. Do not turn reasoning into bullet fragments.
- Keep pages focused: if a page needs a second topic, it needs a second page.

## Code and commands

- Every code block names its language (`c`, `ini`, `console`, `bash`,
  `makefile`).
- Every snippet comes from a tested file through the snippet include, never
  pasted. **(lint: untagged code block in a guide)**
- Commands the reader types use a `bash` block with no prompt. Use a
  `console` block with `$ ` only when you show the output too.
- Show expected output after commands whenever it fits in a few lines.
- File names, flags, register names and identifiers go in backticks.

## Facts that change

- Never write a version number, a device count or a device list in prose.
  **(lint: version pattern in prose)** Link the generated page instead:
  supported devices, HAL modules, boards, CLI flags, versions.
- Never restate a fact another page owns; link to it.
- When a statement depends on the release (for example "supported in 1.0"),
  link the "What's in 1.0" page.

## Links

- Across repositories: absolute links to the hub.
- Inside one repository: relative links.
- Link text says where it goes ("see the UART module reference"), never
  "click here".
- Registry text: absolute links only.

## Punctuation and formatting **(lint)**

- No em-dash characters anywhere; use a colon, a comma, parentheses or a new
  sentence.
- Oxford comma in lists of three or more.
- Numbers: digits for 10 and above and for all measurements and counts
  (`8 KB`, `4 MHz`); units with a space.
- Bold only for the one term a paragraph defines; italics sparingly.

## Admonitions

Use at most one per section, and only these:

- **Note** for useful context the reader may skip.
- **Warning** for something that can damage hardware or lose work.
- **Tip** for a faster or better way.

## Images and diagrams

- Every image has alt text that says what it shows.
- Diagrams are text-based (Mermaid) where possible, so they diff and stay
  current.
- Screenshots only for UI that cannot be shown as text, with the version
  in the alt text.

## Before you open a PR

- The page is one kind (tutorial, how-to, reference or explanation).
- Every command and snippet comes from a tested file.
- No version strings, device lists or XC8 numbers in prose.
- The prose lint and the link check pass.
