# Importing a DOSBox conf

Because the config schema *is* the DOSBox conf model, a real `dosbox.conf` can be read
straight into a game's config. That is the shortest path to a DOS extension of your own:
collect the games and their conf files, then import the confs rather than re-entering
hundreds of settings by hand.

There are two ways it happens.

### Automatically, on install

When a game is installed, Junk Store Pro looks for conf files and imports them without being
asked. It searches these locations under the game directory:

```
<gamedir>/
<gamedir>/app/
<gamedir>/gog-support/app/
<gamedir>/gog-support/<shortname>/app/
```

Every `.conf` file found in those directories is parsed and **merged**, so a game shipping
several confs ends up with the union of them.

The import runs when any of these is true: a `DOSBOX` directory exists in the game directory,
a conf file is found in `app/` or `gog-support/app/`, or the game's executable path contains
`dosbox`.

Note it runs **regardless of which launcher is selected**, deliberately, because a game can
support both ScummVM and DOSBox and you may switch between them. If both are present ScummVM
is chosen as the platform, but the DOSBox settings are still imported and waiting.

So for a DOS extension, if you lay games out the way the shipped ones do, the settings import
themselves. That is the least work path and worth designing your `getlisting` and installer
around.

### Manually, from the file manager

For a conf that is not in one of those locations, or one you want to apply on your own terms,
import it by hand:

1. Open the file manager and browse to the `.conf` file.
2. Open the context menu on it and choose **Import DOSBox Config**.
3. Pick an import strategy and a target fork.
4. Confirm.

The menu entry appears for any file ending in `.conf` or `.config`.

**Import strategies:**

| Strategy | Effect |
|---|---|
| Merge with existing | Combines the file with the game's current config. Values in the file win, anything not mentioned is left alone. The default, and usually what you want |
| Replace existing | Discards the current config and uses the file's contents alone |
| Autoexec only | Takes just the `[autoexec]` block and leaves every other setting untouched |

**Autoexec only** is the useful one when a game runs correctly but needs different startup
commands, since it lets you change the mount and launch lines without disturbing tuning you
have already done.

**Target fork** decides which config set receives the import:

| Choice | Stored against |
|---|---|
| All forks (default) | The platform generally, so it applies whichever DOSBox fork is used |
| DOSBox | Only the `dosbox` fork |
| DOSBox-X | Only the `dosboxx` fork |
| DOSBox Staging | Only the `staging` fork |

This is where the config set tagging described in
[Config layering](../concepts/config-layering.md) becomes practical. DOSBox-X and Staging
accept settings the original does not, so importing a Staging tuned conf against the
`staging` fork keeps it from breaking the others. You can import several confs for the same
game, each against a different fork, and Junk Store Pro picks the right one when the game runs.

The dropdown offers those three named forks. A fork of your own is not in the list, so import
against **All forks** and adjust from the config screen afterwards, where the fork field can
be typed by hand.

### What gets imported

Sections and their `key=value` options become config fields, and the `[autoexec]` block
becomes the Autoexec text.

A setting Junk Store Pro has never heard of is kept, not discarded. Any `key=value` line inside a
section becomes a field, so a conf written for a fork with its own settings imports intact.
That is what makes this a workable route for a custom DOS setup: you are not limited to the
keys Junk Store Pro happens to know.

Two things are dropped:

- **Comments.** Lines beginning with `#` are skipped, so a commented conf loses its notes on
  import. Keep the original file if the comments matter to you.
- **Blank lines**, which are only formatting.

Values may contain `=`; only the first one separates key from value. Keys and values are
trimmed of surrounding whitespace.

After importing, open the game's config screen to see the result. Everything is editable
there, so the import is a starting point rather than a commitment.

## This is an INI reader, not a DOSBox reader

This is one of the emergent cases described in
[Some of what it does is emergent](../concepts/the-generator.md#some-of-what-it-does-is-emergent):
nobody set out to write a general INI importer, and one appears to have fallen out of writing
a DOSBox one.

A `dosbox.conf` is an ordinary INI file:
`[section]` headers, `key=value` pairs, `#` comments, plus one section that holds raw lines
rather than pairs. The importer matches exactly that and nothing more. There is no list of
DOSBox settings, no validation against known keys, and nothing that inspects the file to
decide whether it is really a DOSBox conf.

So **any INI shaped file should import**, and the section above already relies on that: the
reason an unknown setting survives is that the reader was never checking names in the first
place. A config for an emulator, a game's own settings file, or a tool that happens to use
INI would come through as sections and fields the same way.

**This is untested, and the export side is not symmetric.** Two things to know before relying
on it:

- **`autoexec` is special only by name.** A section called `autoexec` has its contents taken
  as raw text rather than as key and value pairs. In a file where `autoexec` means something
  else, that section would not import as fields.
- **Writing a conf back out always appends an `[autoexec]` section**, whether the original had
  one or not. So a round trip through import and export is faithful for DOSBox and adds a
  section for anything else.

Treat it as a promising direction rather than a supported feature. If you try it and it works
for a format that matters to you, that is worth reporting: a real use case is what tends to
turn something like this into a documented capability.

