# Internals

Design history for maintainers: why each repository is the way it is. Start here if you want the reasoning behind a decision, then follow the link to the repository that owns it. User pages never link here.

Each repository keeps its own internals next to its code, with an index and a migration map of every moved page:

- [epic-cc internals](https://github.com/apojomovsky/epic-cc/blob/master/docs/internals/index.md): compiler design notes, decision records and specs.
- [epic-hal internals](https://github.com/apojomovsky/epic-hal/blob/master/docs/internals/index.md): experiment write-ups, measurement records and design specs.
- [epic-platformio internals](https://github.com/apojomovsky/epic-platformio/blob/master/docs/internals/index.md): platform decisions and maintainer packaging notes.
- [epic-tools internals](https://github.com/apojomovsky/epic-tools/blob/master/docs/internals/index.md): where the packaging records live; this repository keeps no separate design history.

Old links redirect through the [aggregate migration map](MIGRATION.md).

## Writing docs

Every page follows the [style guide](style-guide.md). Page templates live in the hub repository's `templates/` directory.
