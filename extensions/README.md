# Junk Store extensions

Extensions are how Junk Store learns about new places your games come from: a
storefront, an emulator, a folder of ROMs, a collection of DOS games. Everything
you see in the Junk Store tabs (Epic, GOG, Amazon, Itch) is an extension.

**This is documentation for people writing them.** It covers the contracts an extension has
to satisfy: which scripts get called and when, what they receive, what they must print, how
configuration is declared and resolved, and how a game gets launched. The reference sections
are the authority; the guides are worked examples of using them.

It is readable without being a developer, and much of it needs no code at all, since an
extension can be set up entirely through the wizard and settings. But it is written for
someone building something, and it does not stop to explain shell scripting or the basics of
the interface. If a word here is unfamiliar, the
**[glossary](../glossary.md)** explains the vocabulary in plain language.

Nothing here requires a compiler, a git checkout, or development tools.

New here? **[Introduction](introduction.md)** explains what an extension is, why the system
works the way it does, and where the odder parts came from. Worth ten minutes before the
guides.

**[Workflows](workflows.md)** walks four common jobs end to end and shows how the pieces hand
off to each other. Useful for orientation before the reference sections, and it ends with what
the shipped extensions actually contain, which is the best guide to what yours will need.

## Guides

Read these in order the first time. Each one takes you through a whole task.

| Section | For |
|---|---|
| [Quick start](guides/quickstart.md) | Creating a new extension, the recommended starting point |
| [Overriding actions](guides/overriding-actions.md) | Changing how one action behaves on an existing store |
| [Authoring by hand](guides/authoring-by-hand.md) | Writing an extension's scripts yourself, for full control |
| [Emulators and ROM discovery](guides/emulators-and-roms.md) | Setting up an emulator and getting your ROMs to show up |
| [When a game will not run](guides/when-a-game-will-not-run.md) | Finding out why a game does not start, without leaving game mode |

## Concepts

Read one of these when you need to understand how a mechanism works, rather than
to look something up.

| Section | Explains |
|---|---|
| [How Junk Store finds your extension](concepts/how-extensions-are-found.md) | Discovery by directory and naming convention |
| [How launching works](concepts/how-launching-works.md) | The path from the Steam shortcut through `launcher.sh` to a platform scriptlet |
| [The config schema format](concepts/config-schema.md) | The structure every config screen is built from, and its DOSBox origins |
| [Config layering](concepts/config-layering.md) | Which stored config applies to a game, and how values reach your scripts as environment variables |
| [The Generator](concepts/the-generator.md) | The configuration entries an extension gets, and what generation actually produces |

## Reference

Look these up while you work.

| Section | Contains |
|---|---|
| [Custom scripts](reference/custom-scripts.md) | Every hook, with its arguments, stdin, and stdout |
| [Script output](reference/script-output.md) | The label and JSON conventions scripts print |
| [static.json](reference/static-json.md) | The file that puts an extension on screen, and how fragments merge |
| [Downloader protocol](reference/downloader-protocol.md) | Progress keys, where each appears on screen, and the junklib parsers |
| [Settings](reference/settings.md) | What each setting in the tab and game config does |
| [Actions, results, and types](reference/actions-and-types.md) | Action names, result shapes, action and field types |
| [Download methods](reference/download-methods.md) | Choosing between script, rsync, and none |
| [Importing a DOSBox conf](reference/dosbox-import.md) | Reading a real `dosbox.conf` into a game's config |
| [Sharing and licensing](reference/sharing-and-licensing.md) | Export, import, source control, and what you may share |

## When something is wrong

[Troubleshooting](troubleshooting.md) covers why a change did not take effect, and
where to look when a script does not behave.

## The three ways to change things

Junk Store offers three levels. Picking the right one saves a lot of effort, and
most people never need the deepest one.

**Level 1: the wizard and settings.** Point and click inside Junk Store. The
Generator's extension wizard creates a working extension from a few answers, and the
cog menu adjusts its settings afterwards. This covers most emulator and "folder of
games" cases. No files, no scripts.
See [Quick start](guides/quickstart.md).

**Level 2: an override.** You like an existing store but want one action to
behave differently, such as an extra step before install. You drop a small shell
file in one place and Junk Store picks it up. The original extension is untouched,
so updates will not clobber your change. Note this covers actions, not launching.
See [Overriding actions](guides/overriding-actions.md).

**Level 3: hand authored scripts.** You are building something the settings
cannot express: a new storefront with its own login, a custom downloader, unusual
install logic. You write the shell scripts yourself and register them.
See [Authoring by hand](guides/authoring-by-hand.md).

Start at the lowest level that does what you need. You can always move up. An
extension set up from a preset can be hand edited later.

## Where your things live

Two directories matter. Both are inside your home folder, and neither needs root.

```
~/.local/share/junkstore/scripts/Extensions/<Store>/
    The scripts Junk Store actually runs for a store.

~/.config/junkstore/
    Your settings, databases, and overrides.
    overrides/<Store>/store.sh   <- your personal changes go here
```

Older notes and some strings inside Junk Store mention a `homebrew` directory.
That is historical and can be ignored. Junk Store only uses the two paths above.

## Sharing your work

An extension can be exported to a single `.json` file and imported by someone
else. See [Sharing and licensing](reference/sharing-and-licensing.md).

**Only import extensions from people you trust.** An extension is executable code, not a
settings file, and it runs as you with no sandbox. Importing one is closer to running a shell
script somebody sent you than to loading a configuration. See
[Only import extensions from people you trust](reference/sharing-and-licensing.md#only-import-extensions-from-people-you-trust).

**Open to read and change is not the same as redistributable.** Nothing is compiled or
hidden, so you can read the shipped extensions, modify your own copy, and learn from how they
work. What you may not do is pass their code on: Epic, Amazon, GOG, and Itch are source
available rather than open source. Extensions you create are entirely yours to share. An
export is a complete copy of whatever it contains, so this applies to a `.json` export as
much as to the scripts. See
[What you may and may not share](reference/sharing-and-licensing.md#what-you-may-and-may-not-share).

## A note on completeness

This documentation was written by working through the source, and is a first pass at
material that had not been documented before. It is accurate where it makes a claim, but
it is not complete. If something you need is missing or wrong, say so.
