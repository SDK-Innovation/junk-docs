# Settings reference

What every setting in the tab config and game config does.

**About the defaults listed here.** These are the **raw** defaults: what a setting is worth
when nothing else has set it. They are the right thing to know for understanding a field,
but they are frequently **not** what your extension actually has.

Generation writes its own values on top, so an extension created by the wizard starts with
the Generator's choices rather than these. An emulator extension, for example, arrives with
the data source, artwork settings, and download method already set to something other than
the values below.

Use this reference to learn what a setting means. To find out what it is currently set to, look
at the extension itself, or ask Junk Store for the resolved value. See
[Settings and environment variables](../concepts/config-layering.md#seeing-the-result).

## Finding settings: the visibility dropdown

Most settings are hidden by default. At the top of a configuration screen there is
a dropdown that controls how much you see:

| Level | Shows |
|---|---|
| Basic | Only the everyday settings |
| Advanced | Basic, plus per extension behaviour |
| Expert | Advanced, plus emulator and platform internals |
| All | Everything, including rarely touched fields |

If a setting named here is not on screen, raise the level. Each field
below is tagged with the lowest level that reveals it.

Sections themselves are also levelled, so a whole section can be hidden. The
`WGET`, `RSYNC`, and `RetroArch` sections are hidden until you reach the level they
need.

## Editing a field by hand

Every field in a config editor can be edited as free form text, whatever control it
normally shows. This is the escape hatch when the dropdown does not offer the value
you need, or when a field expects something the control cannot express.

**Press Y on the field** to open a text editor for it. Type whatever you want and it
is saved as the field's value. This works on toggles, dropdowns, numbers, and paths,
not just text fields, so you are never limited to the choices presented.

Two related gestures on a field:

| Input | Effect |
|---|---|
| Y | Open the text editor and type the value directly |
| Start | Reset that field to its default value |

### Start resets one field, or all of them

The same button does both, and which you get depends on what is focused:

| Focus | Start does |
|---|---|
| A field | Resets that field |
| The visibility dropdown at the top | Resets **every value in the configuration** |

**Default means the extension's own default, not empty.** Each field is restored to the
`DefaultValue` it was generated with, so an extension whose defaults were set properly in the
Generator resets to a working configuration rather than a blank one. That is the case it is
designed for.

What it discards is everything set on top of that: the adjustments you made through this
screen after the extension was generated. If those matter, so does the confirmation dialog.

Two things soften it. The dialog is asked first, and **nothing is written until you save**, so
a reset you did not mean can be abandoned by backing out and choosing **Discard** at the
Unsaved Changes prompt. Once saved, there is no undo.

**The cog on a field changes its type.** If a field is presenting the wrong kind of
control for what you need, you can switch it between Boolean, Number, String, List,
File, and Directory. Range is offered when the field has a usable minimum and
maximum, and List when it has values to choose from.

This is genuinely useful and genuinely sharp. Typing a value by hand skips whatever
validation the normal control provides, so a malformed value will reach the scripts
as you typed it. If something stops working right after you edited a field this way,
press Start on it to restore the default.

## Two places settings live

**Tab config** applies to the whole store, meaning every game in that tab. Reached
from the cog menu on the store's tab.

**Game config** applies to one game and overrides the tab setting where both
exist. Reached from the game's own configuration.

The game config carries a smaller set: `RetroArch`, `Advanced`, and `ENVIRONMENT`.
Everything else is tab level only.

## General

Settings that control how the store behaves day to day.

| Setting | Type | Default | Level | What it does |
|---|---|---|---|---|
| Install Location | Enum | `SSD` | Basic | Where new games install: `SSD` (internal), `MicroSD` (card), or `Other` to use your own path |
| Custom Install Path | Directory | `/home/deck` | All | The path used when Install Location is `Other` |
| Install Directory | String | `Games/<Store>` | All | Where inside the install location games go. Absolute path if Install Location is `Other`, otherwise relative to home or the SD card mount point |
| Roms in root | Boolean | `true` | Basic | Whether ROMs sit directly in the folder rather than each in its own subfolder named after the ROM |
| ROMS Extension | Enum | `iso` | All | The file extension of your ROMs. Choices: `zip`, `iso`, `7z`, `nes`, `sfc`, `z64`, `gbc` |
| Download Extension | Enum | `zip` | All | The file extension of downloaded files, same choices as above |
| Download method | Enum | `script` | All | How games are fetched: `script` (the extension's own downloader), `rsync`, or `none` |
| Enable Run Exe in Game Dir | Boolean | `True` | All | Lets you browse for and run executables inside the game directory |

## Advanced

Per extension behaviour. Several of these change which actions appear in the UI,
not just how they work.

| Setting | Type | Default | Level | What it does |
|---|---|---|---|---|
| Show installation options | Boolean | `true` in the schema | Expert | Show the installation options popup before installing. The shipped extensions do not present it, because running the four scripts delays every install and their defaults are almost always right. Turn it on when you need to choose DLC, languages or dependencies per install |
| Needs Login | Boolean | `false` | All | Adds login and logout actions for this store |
| Has bat files | Boolean | `false` | All | Adds an editor for the `.bat` files stored against a game, used for DOS and old Windows games. See below |
| Has pre installation settings | Boolean | unset | All | The store has settings to present before install |
| platform | Enum | empty | Advanced | Which launcher to use. Choices come from the launchers installed on your system, for example Proton or Linux. Setting this to a Proton or Linux value also adds the Proton related actions |
| platform-version | String | empty | Advanced | A specific version of the chosen platform |
| platform-fork | Enum | empty | Advanced | A variant of the platform: `dosbox`, `dosboxx`, `staging`, or blank |
| Data source | Enum | empty | All | Where artwork and metadata come from. `Libretro` uses RetroArch thumbnails; the rest are platform identifiers used for artwork lookup. Only `Epic`, `Gog`, and `Amazon` additionally drive Proton compatibility id assignment; every other value is artwork only |
| Base Url | Enum | empty | All | Base URL the extension downloads content from |
| Url encode | Boolean | `false` | All | URL encode arguments passed to URLs |
| Use proxy cache for images | Boolean | `false` | All | Fetch images through the local proxy cache instead of directly |
| image-prefix | Enum | empty | All | Prefix for image lookups, used with RetroArch thumbnail paths |
| store-url | String | empty | All | The store's web address |
| Use Legacy Clients | Boolean | `false` | Expert | Use the older flatpak clients such as Legendary instead of the built in native clients |
| Enable Cloud Saves | Boolean | unset | All | See the warning below |

### About Has bat files

The `.bat` files are held **in the game's database record**, not read from the install
directory when the game runs. They get there by being imported, from the file manager's
context menu on a `.bat` file, in the same way a `dosbox.conf` is imported. The actions this
setting adds then read them back out for editing and save your changes to the record.

Worth knowing because it means editing the file on disk and editing it here are two different
things. This is the same round trip described in
[Importing a DOSBox conf](dosbox-import.md), applied to batch files.

### About Enable Cloud Saves

This setting carries an explicit warning in the software itself: enabling it is
likely to lose or corrupt save games, and no support is offered if it goes wrong.
Leave it off unless you are willing to accept that risk and manage your own
backups.

### About Data source

The value is used as a platform slug when looking up artwork and metadata. There
is a long list, covering PC stores (`Steam`, `Epic`, `Gog`, `Amazon`, `Origin`,
`Uplay`, `Battlenet`, `Itch`, `Humble` and many more), game specific launchers
(`Ffxiv`, `Minecraft`, `Pathofexile` and similar), modern consoles (`Psn`,
`Xboxone`, `Nswitch`, `Psp`, `Psvita`, `Nds`, `3ds`), older consoles (`Ps2`,
`Psx`, `N64`, `Nwii`, `Ncube`, `Dc`, `Saturn`, `Jaguar`, `3do`) and retro systems
(`Snes`, `Nes`, `Sms`, `Segacd`, `Neo`, `C64`, `Zx`, `Atari`, `Amiga`).

Pick the platform your games actually belong to and artwork lookups will match.
`Libretro` is the special case: it uses the RetroArch thumbnail repository instead.

## ENVIRONMENT

Environment variables passed to the game, mainly for Proton and umu behaviour.

| Setting | Type | Default | Level | What it does |
|---|---|---|---|---|
| HOST_LC_ALL | Enum | empty | All | Host locale, for example `en_US.UTF-8`. Use when a game needs a specific language |
| LANG | Enum | empty | All | Language for the game, same choices as above |
| Umu Store Name | Enum | empty | All | Which store umu should present itself as, which can affect game specific fixes. Choices include `amazon`, `battlenet`, `ea`, `egs`, `gog`, `humble`, `itchio`, `steam`, `ubisoft`, `zoomplatform` |
| Toggle offline mode | Boolean | `false` | Basic | Run the game in offline mode |

Available languages for the locale settings are English, German, French, Italian,
Spanish (Spain), Portuguese (Brazil), Japanese, Chinese Simplified, Korean,
Polish, and Russian.

## RetroArch

Only relevant for emulated games. This section is hidden until Expert level.

| Setting | Type | Default | Level | What it does |
|---|---|---|---|---|
| Cores location | Directory | RetroArch flatpak cores path | All | The directory holding your RetroArch cores. The default points at the flatpak install |
| RetroArch Core | Enum | empty | Expert | Which core runs this game. The list is a catalogue of known cores, not a list of what you have installed |

A core you do not have yet is downloaded automatically on first launch, so you can
select any core in the list. Make sure **Cores location** points at your real
RetroArch cores directory, or the download will land where RetroArch cannot see it.
See [Emulators and ROM discovery](../guides/emulators-and-roms.md#retroarch-cores).

At the system level there is also a `RetroArch System` setting, which selects the
system rather than the individual core.

## RSYNC

Used when Download method is set to `rsync`. Hidden until All level.

| Setting | Type | Default | What it does |
|---|---|---|---|
| Use SSH | Boolean | `true` | Tunnel rsync over SSH |
| SSH User | String | `user` | Username on the remote machine |
| SSH Host | String | `127.0.0.1` | Address of the remote machine |
| SSH Port | String | `22` | SSH port |
| ROMS Path | Directory | `/home/deck/roms` | Path on the remote machine holding the games |

## WGET

A place to keep a base URL for an extension that downloads over HTTP. Hidden until All level.

| Setting | Type | Default | What it does |
|---|---|---|---|
| Base url | String | `http://localhost/` | The base URL to download from |

**This section is available to any extension and is in use today.** It reaches your scripts as
`WGET_BASE_URL`, like every other setting, and a `script` downloader can read it and fetch
from it however it likes.

What it is *not* is a built in download method. A fourth method was planned around this
section and dropped, because a script already does the job; the setting stayed because a
downloader still needs somewhere to keep its base URL. See
[A note on other methods](download-methods.md#a-note-on-other-methods).

## Generator placement settings

These control where your extension appears in the Junk Store interface, and are
set on the extension in the Generator rather than per store.

| Setting | Type | Default | Level | What it does |
|---|---|---|---|---|
| Group Name | Enum | `Custom Stores` | All | The section your extension is listed under: `Custom Stores`, `Emulators`, or `Other` |
| Section name | Enum | `Games` | All | The button your extension appears under, which is a collection of tabs: `Games`, `Nintendo`, `Sega`, `Nec`, or `Tools` |

## Tab config versus game config

Where a setting exists in both, the game value wins for that game. The game config
contains:

- **RetroArch**: core selection for this specific game
- **Advanced**: `platform`, `platform-version`, `platform-fork`, and
  `Enable Cloud Saves`
- **ENVIRONMENT**: the locale, umu store, and offline mode settings

This is how you run one game under a different Proton version, or with a different
emulator core, without changing the whole store.

## After changing a setting

Settings that affect generated scripts need a regenerate to take effect. See
[the regenerate step](../guides/quickstart.md#the-one-step-people-forget-regenerate).
