# Contributing

Corrections are welcome, particularly where something is **wrong** rather than
merely missing. This documentation was written by working through the source and
is a first pass, so errors are expected and worth reporting.

Useful contributions, roughly in order of how much they help:

- A claim that is incorrect. These matter most: the reference sections are meant
  to be authoritative, so a wrong statement is worse than a missing one.
- A step that does not work as described, or a command that fails.
- A screenshot that is out of date, or one that would explain something the prose
  is labouring over.
- Typos and broken links.

Open an issue if you would rather just report something. That is a perfectly good
contribution and does not require any of what follows.

## Making a change

The documentation is plain markdown with relative links between files. There is no
build step to run before submitting, and no toolchain to install.

To check a change renders, build the PDF:

```bash
./build-pdf.sh
```

That needs `python3` and either `chromium` or `google-chrome`. It writes a copy to
a temporary directory and never modifies the markdown.

If you add a page, add it to the `PAGES` list in `build-pdf.sh` in reading order,
and link it from the section's `README.md`.

## Screenshots

Screenshots are captured from a live Steam Deck, so please check what is visible
before submitting one: account names, avatars, real file paths, library contents,
and anything else personal to your device. Crop or retake rather than submit a
shot you are unsure about.

## Sign-off

This project uses a Developer Certificate of Origin. It is a single line in your
commit message stating that you wrote the contribution, or otherwise have the
right to submit it under this project's licence:

```
Signed-off-by: Your Name <your.email@example.com>
```

`git commit -s` adds it for you.

There is no separate agreement to sign. You keep the copyright in what you write;
the sign-off confirms you are contributing it under the licence below, which is
what lets it be distributed as part of the documentation.

The full text is at <https://developercertificate.org/>.

## Licence

This documentation is licensed **CC BY-ND 4.0** (Attribution, NoDerivatives). See
[LICENSE](LICENSE). Contributions are accepted under the same terms.

NoDerivatives restricts distributing *modified* versions, which is the point: it
prevents the documentation being rewritten and republished as something else. It
does not restrict contributing here, quoting it, or linking to it.

**Translations are welcome** despite the NoDerivatives term. A faithful
translation is granted an explicit exception, provided it credits the original,
links back to this repository, and states that it is a translation. Open an issue
before starting a substantial one, so effort is not duplicated.

A note on scope: the shipped Junk Store Pro extensions (Epic, Amazon, GOG, Itch) are
source available rather than open source, and that is unrelated to this licence.
This repository covers the documentation only. See
[Sharing and licensing](extensions/reference/sharing-and-licensing.md#what-you-may-and-may-not-share)
for what applies to extension code.
