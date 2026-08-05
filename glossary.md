# Glossary

Words that come up in Junk Store and in this documentation, in plain language.

You do not need to read this. It is here so that if you meet a word you do not
know, particularly if you have wandered into the developer documentation, there
is somewhere to look it up.

Terms are grouped by where you are likely to meet them rather than
alphabetically, since related words are easier to understand together.

---

## Things you see in Junk Store

**Extension**
: The part of Junk Store that knows about one place your games come from. Epic,
GOG, Amazon and Itch are extensions, and so is a folder of DOS games you set up
yourself. Each one appears as its own tab. If you have ever installed a browser
add-on, the idea is the same: the main program stays the same, and extensions
teach it about new things.

**Store**
: Usually the same thing as an extension, seen from the outside. The extension is
the machinery; the store is what you see. The documentation uses "store" when it
means the tab you click and "extension" when it means the files behind it.

**Tab**
: The row of names along the top of Junk Store. One per extension, plus the
Generator and the download queue. Those last two are extensions as well, built on
the same machinery as the rest.

**The Generator**
: The tab where extensions are created and configured. It holds the wizard for
making a new extension, the list of extensions you have installed, and the
editors behind them. Most people use it to download official extensions and
nothing else.

**Wizard**
: The guided set of questions in the Generator that builds a working extension
from your answers. Aimed at simple cases, such as an emulator and a folder of
games. No files, no scripts.

**Preset**
: A ready-made extension you can download rather than build. The presets on the
server are the official Junk Store ones, such as Epic and GOG. An extension
someone else wrote is not a preset and arrives as a file instead.

**Settings and configuration**
: The options behind the cog menu on a tab. Most are hidden until you raise the
visibility level from Basic to Advanced, Expert or All, because most people never
need them.

**Side menu**
: The panel that slides in when you press SELECT, holding the things that are not
specific to the game you are looking at.

---

## Games and how they run

**Launcher**
: The thing that actually starts a game. Different games need to be started
differently: a Windows game needs Proton, a DOS game needs DOSBox, a console game
needs an emulator. The launcher is whichever of those applies.

**Platform**
: Junk Store's word for which launcher a game uses. Setting a game's platform to
`Proton` means "start this with Proton". The shipped ones include `Proton`,
`Linux`, `Dosbox`, `RetroArch`, `ScummVM`, `Dolphin`, `Ryujinx` and `Yuzu`.

**Proton**
: Valve's software for running Windows games on Linux. The Steam Deck runs Linux,
so nearly every Windows game you play on it is running through Proton. It is
built on Wine, and you can mostly treat the two names as the same thing.

**Wine**
: The long-standing open source project for running Windows programs on Linux.
Proton is a version of Wine that Valve maintains for games.

**Prefix**, sometimes **Wine prefix**
: A private folder that pretends to be a Windows installation, holding the fake
C: drive, the registry and the settings for one game. Each game normally gets its
own, which is why one game's Windows quirks do not affect another.
**A Windows game's saved games usually live in here**, so a prefix is worth
looking inside before you delete it. Deleting the prefix is a common fix when a
game misbehaves, but it takes the saves with it unless you copy them out first.

**ROM**
: A copy of a game from a cartridge or disc, as a file on disk. Emulators run
these. Junk Store never supplies them; you point it at ones you already have.

**Emulator**
: A program that imitates older hardware so its games can run. RetroArch, Dolphin
and ScummVM are emulators.

**DOSBox**
: An emulator for MS-DOS, which is how DOS-era PC games are played today.
DOSBox-X and DOSBox Staging are alternative versions of it, with more features.

**Shortcut**
: An entry in your Steam library. Junk Store adds one per installed game, so games
it manages appear in your library and can be launched from there like anything
else.

---

## The Steam Deck itself

**Game Mode**
: The controller-driven interface the Deck starts in. Junk Store runs inside it.

**Desktop Mode**
: The ordinary Linux desktop, reached from the power menu. Some operations are
easier there because you have a keyboard, a mouse and a terminal.

**Terminal**, or **command line**
: A window where you type commands rather than clicking. A few Junk Store
operations are deliberately only available this way, importing an extension being
the main one, because it makes them slow enough to think about first.

**SSH**
: A way of connecting to another machine over the network to run commands on it.
Used for putting games on a server rather than the Deck itself, and for reaching
your Deck from a computer.

**SSH key**
: A pair of files that proves who you are to another machine, used instead of a
password. The *private* half stays on your machine and should be guarded like a
password. The *public* half is copied to machines you connect to, and is safe to
share. Junk Store authenticates this way because a password cannot be typed from
Game Mode.

**authorized_keys**
: The file on a machine listing the public keys allowed to connect to it. Pairing
adds a key here; removing a trusted key takes it out again.

**Pairing**
: Granting one machine access to another, by comparing a six digit code shown on
both and accepting. What it grants is SSH access to the whole user account, not
only to Junk Store.

**Flatpak**
: A way of packaging Linux applications so they run anywhere, bundling what they
need. Some emulators are installed as flatpaks.

---

## Words from the developer documentation

You will only meet these if you have opened the extension documentation. They are
here so it is readable, not because you need them.

**Script**
: A text file of commands that a computer runs in order. Junk Store extensions are
built from scripts, which is why they can be read and changed without any
development tools.

**Shell**, and **shell script**
: The language those commands are written in. The same language you would type in
a terminal.

**`store.sh`**
: The main script of an extension, the entry point everything else goes through.

**`static.json`**
: The file describing what an extension puts on screen: its tab, and where it is
grouped.

**Scriptlet**
: A small script handling one platform's launch, one per platform in the
`launchers/` folder. Editing a scriptlet changes how games on that platform start.

**Action**
: One operation an extension can perform, such as installing a game, launching it,
or listing what is available. Buttons in the interface trigger actions.

**ActionSet**
: A named group of actions belonging together, such as the set behind one screen or
one wizard. Actions are addressed by set and name rather than by name alone, so two
parts of an extension can each have their own "install" without colliding. When the
interface opens something it names the set it is working in, and every action it then
offers is looked up inside that set.

**Override**
: A small file of your own that changes how one action behaves, without touching
the original extension. Your change survives updates because the extension is left
alone.

**Generate**, or **regenerate**
: Junk Store stores an extension's definition in a database and writes the actual
scripts out from it. Regenerating is that writing-out step. Changing a setting or
a script does not take effect until you regenerate, which is the single most
common reason a change appears to do nothing.

**Fork**
: A variant of a runtime that behaves differently enough to need its own
configuration, such as DOSBox-X alongside DOSBox.

**Shortname**
: The identifier an extension uses for one game, its key in the database.

**Commandmap**
: The editor in the Generator listing an extension's actions and how each is run.

**Database**
: A file storing structured information. Junk Store keeps its extension
definitions, your games and their settings in several of these.

**JSON**
: A text format for structured data, used for configuration files and for what
scripts print back to Junk Store. Readable, if fussy about punctuation.

**CLI**
: Command Line Interface. A program you drive by typing rather than clicking.

---

## Related

- What an extension is and why the system works this way:
  [Introduction](extensions/introduction.md)
- Getting started:
  [Quick start](extensions/guides/quickstart.md)
- When something is not working:
  [Troubleshooting](extensions/troubleshooting.md)
