# Junk Store documentation

Documentation for [Junk Store](https://junkstore.xyz), a game launcher for the Steam Deck.

Each top-level directory is a section, written to be read on its own.

| Section | For |
|---|---|
| [Using Junk Store](user/) | Using the product: the File Manager, and how to get things done day to day |
| [Extensions](extensions/) | Writing extensions: the scripts Junk Store calls, what they receive, what they print, and how configuration reaches them |

[**Glossary**](glossary.md) — the vocabulary used across all of it, in plain language.
Start here if a word is unfamiliar.

## Building the PDF

Any section can be rendered as a single PDF. This builds the extension documentation:

```bash
./build-pdf.sh                       # extensions -> junk-store-extensions.pdf
./build-pdf.sh user                  # user       -> junk-store-user.pdf
./build-pdf.sh user /path/to/out.pdf
```

The glossary is appended to every section, since it serves all of them.

Needs `python3` and either `chromium` or `google-chrome`. The script is read-only:
it renders a copy in a temporary directory and never modifies the markdown.

## Contributing

Corrections are welcome, particularly where something is wrong rather than merely
missing. This was written by working through the source and is a first pass, so
errors are expected and worth reporting. Opening an issue is a perfectly good
contribution.

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

Copyright © 2026 SDK Innovation Ltd.

This documentation is licensed under
[CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/) (Attribution,
NoDerivatives). You may share it, in any medium or format, including commercially,
provided you credit the source. You may not distribute modified versions.

Faithful translations are granted an explicit exception. See
[CONTRIBUTING.md](CONTRIBUTING.md#licence).

This covers the documentation only. Junk Store's shipped extensions are source
available rather than open source, which is a separate matter. See
[Sharing and licensing](extensions/reference/sharing-and-licensing.md#what-you-may-and-may-not-share)
for what applies to extension code.
