# Emulators and ROM discovery

A worked walkthrough of the most common case: getting a folder of ROMs showing up as
a store, using the extension wizard. This expands on
[Quick start](quickstart.md) with the emulator specific detail.

## What you need before you start

- Your ROMs in one place. A folder on the device, on an SD card, on a mounted
  external drive, or on a remote machine you can reach over SSH.
- **The emulator installed as a flatpak.** See below, this is the most common reason a
  game will not launch.

### The emulator must be installed

Junk Store does not bundle emulators. It runs them, which means the flatpak has to be
on the system already. Each launcher calls a specific flatpak:

| Launcher | Flatpak |
|---|---|
| RetroArch | `org.libretro.RetroArch` |
| Dolphin | `org.DolphinEmu.dolphin-emu` |
| Dosbox | `com.dosbox.DOSBox` |
| ScummVM | `org.scummvm.ScummVM` |
| Ryujinx | `org.ryujinx.Ryujinx` |
| Yuzu | `org.yuzu_emu.yuzu` |

If you selected the emulators during the Junk Store Pro installation, they are already
there. If you skipped that step, or you want one you did not pick at the time, install
it yourself:

1. Switch to Desktop Mode.
2. Open **Discover**, the software store.
3. Search for the emulator and install it.
4. Return to Gaming Mode.

Installing through Discover gets you the same flatpak the launcher expects, so nothing
else needs configuring afterwards.

If a game does nothing when you launch it, a missing emulator is the first thing to
check. The `launcher.log` in the game directory will show the `flatpak run` command
that failed. See
[Troubleshooting](../troubleshooting.md#reading-the-logs).

## What the wizard asks, and what each answer sets

The wizard is not just a form. Each answer writes specific configuration, so it helps
to know what you are actually choosing. The questions follow your answers, so you
will not see all of them.

| Question | What it sets |
|---|---|
| Name | The extension and store name, and the install directory `Games/<Name>` |
| Group and section | Where the extension appears in the interface |
| Emulator or system | The launcher platform, and the RetroArch system or core if applicable |
| All ROMs on board? | Whether there is a downloader at all. Answering yes sets the download method to `none` |
| Install on demand? | Turns on `rsync` as the download method |
| Download over SSH? | Whether rsync tunnels over SSH. Answer no when the ROMs are on media the device can already reach, such as an SD card, external drive, or mounted share |
| Remote server details | The SSH user and host. Only asked when copying over SSH |
| ROMs location | The path your ROMs live at, local or on the server depending on the answer above |
| ROM extension | Which file extension counts as a game |
| Zipped? | Whether the downloaded file is a `zip` rather than the raw ROM |
| Generate now? | Whether to build the scripts immediately |

If you answer that your ROMs are already on the device, everything about remote
servers is skipped and you get a simpler extension with no downloader.

## Two shapes of emulator extension

**ROMs already on the device.** The simplest and the recommended starting point. The
extension lists what it finds at your ROMs path. There is no downloader, so nothing
is copied or installed. Choose this if you are unsure.

**ROMs somewhere else, copied in on install.** The extension lists what is available at
another location and copies a game to local storage with rsync when you install it. The
device keeps only what you have installed, which is the point when the library is larger than
the drive.

That "somewhere else" does not have to be a server. With **Use SSH** turned off, the ROMs
path is an ordinary filesystem path, so anything the device can see works:

- An **SD card**, keeping the library off the internal drive.
- An **external drive** over USB, or a dock.
- A **network share already mounted** by the system, whether SMB, NFS, or anything else.
  Junk Store does not care how it got there; from its side it is a directory.

With **Use SSH** turned on, the same two operations run over SSH against a remote host
instead. That needs a reachable SSH server with public key authentication already working,
and Junk Store will not set up keys for you.

The distinction matters because the SSH route is the one with prerequisites. If the media is
something you can already browse to in the file manager, leave SSH off and point the ROMs
path at it.

### Mounting the source yourself

Junk Store does not mount anything. It runs `find` and `rsync` against the path you gave it,
so if that path is not mounted, the listing comes back empty and an install fails.

For removable media that is not always present, you can do the mounting as part of the
operation. Actions generated from the command map support **`script-pre`** and
**`script-post`**, which are shell inserted before and after the action's body, so an install
action can mount before it copies and unmount afterwards:

```bash
# script-pre
mountpoint -q /run/media/roms || mount /run/media/roms
```

```bash
# script-post
mountpoint -q /run/media/roms && umount /run/media/roms
```

See [The Generator](../concepts/the-generator.md#how-script-pre-and-script-post-fit-in) for
where these go and how they wrap the body.

Two cautions before you build on this. Mounting usually needs privileges the plugin does not
have, so this works when the mount is already permitted for your user, through an `fstab`
entry with `user`, an automounter, or a `systemd` unit; it is not a way to gain access you do
not otherwise have. And unmounting in `script-post` will fail while anything still has the
media open, so treat the unmount as best effort rather than guaranteed.

If the media is permanently attached, none of this is necessary. Point the ROMs path at it
and let the system handle mounting at boot.

## How ROM discovery works

Three settings decide which files become games. The wizard sets them from your
answers, and you can change them afterwards in the cog menu.

| Setting | Meaning |
|---|---|
| ROMs Path | Where to look. Absolute path. On the server if you are using SSH, otherwise on your machine |
| ROMs Extension | Which extension counts as a game, for example `iso`, `zip`, `nes`, `sfc`, `z64`, `gbc`, `7z` |
| Roms in root | Whether the ROMs sit directly in that folder, or each in its own subfolder |

**Roms in root** is the one people get wrong. Two layouts:

Roms in root enabled, files directly in the folder:

```
/home/deck/roms/
    Sonic.md
    Streets of Rage.md
```

Roms in root disabled, one subfolder per game:

```
/home/deck/roms/
    Sonic/
        Sonic.md
    Streets of Rage/
        Streets of Rage.md
```

The wizard picks a default based on the emulator, since some expect a folder per game
and others do not. If nothing shows up, this setting is the first thing to check.

Only files matching **ROMs Extension** are picked up. If your folder holds a mix, say
`.md` and `.zip`, you will only see one of them. Set the extension to the one you
actually want to launch.

## Artwork

The wizard configures artwork automatically for emulator extensions, using the
Libretro thumbnail repository:

- **Data source** is set to `Libretro`.
- **Base Url** is set to the Libretro thumbnails address.
- **Use proxy cache for images** is enabled, so images are cached locally rather than
  refetched.
- **image-prefix** is set to the system you chose, since Libretro organises
  thumbnails by system name.

If artwork does not appear, the usual cause is a mismatch between the system name and
the way Libretro names it, or ROM filenames that do not match their database. Artwork
is cosmetic, so it is worth getting the games launching first.

## After the wizard: check these first

1. **Do the games appear?** If not, check ROMs Path, then Roms in root, then ROMs
   Extension, in that order.
2. **Does a game launch?** If not, check the platform is the emulator you meant, and
   that the emulator is actually installed. Launch failures are logged in
   `launcher.log` inside the game directory. See
   [Troubleshooting](../troubleshooting.md#reading-the-logs).
3. **Is the artwork right?** Last, since it does not affect playing anything.

Remember that changes to settings need a regenerate before they take effect. See
[the regenerate step](quickstart.md#the-one-step-people-forget-regenerate).

## Going beyond the wizard

The wizard covers simple launchers. For anything else you edit what it generated:

- **A different emulator command or arguments.** Edit the launcher scriptlet for that
  platform. See
  [Generator settings](../concepts/the-generator.md#launchers-how-games-start).
- **Per game differences,** such as one game needing a different core. Use that
  game's own config, which overrides the store setting. See
  [Settings reference](../reference/settings.md#tab-config-versus-game-config).
- **A source the wizard cannot express,** such as a custom download method. See
  [Authoring by hand](authoring-by-hand.md).

## RetroArch cores

RetroArch extensions have an extra choice: the **core** that runs the game.

**The core list is a catalogue of known cores, not a list of what you have
installed.** Junk Store offers every core it knows about, so you can select one you do
not have yet. That is deliberate, because a missing core is fetched for you on first
launch.

### Cores are fetched on demand

You do not have to install the core yourself. When you launch a game, the launcher
checks whether the selected core is present, and if it is not, downloads it from the
libretro server and unpacks it into your cores directory. The first launch of a game
using a new core therefore takes a little longer, and needs a network connection.

The default cores location is the RetroArch flatpak path,
`~/.var/app/org.libretro.RetroArch/config/retroarch/cores`. If you installed
RetroArch some other way, point **Cores location** at wherever your cores actually
live, otherwise the download lands somewhere RetroArch will not look.

You can also install cores through RetroArch's own online updater if you prefer. Both
end up in the same place, and a core already present is used as is.

### If a core will not load

- **No network on first launch.** The download needs one. Try again when connected.
- **Cores location points at the wrong directory.** The core downloads successfully but
  RetroArch does not find it. Check the setting against your actual RetroArch install.
- **The core name has no matching build.** The catalogue lists known cores, but a given
  core may not have a current build for this platform.

Launch output is recorded in `launcher.log` inside the game directory, and will show
the download attempt and the core path used. See
[Troubleshooting](../troubleshooting.md#reading-the-logs).

You can set a core for the whole store and then override it for individual games that
need a different one.
