# Download methods

An extension's **Download method** decides how games get onto the device, and it changes
more than the transfer itself: it also changes how the games list is discovered. Picking
the right one is most of the work in getting a store to behave.

The setting lives in the General section of the tab config. See
[Settings reference](settings.md).

## The three methods

| Method | Games come from | Listing is built by |
|---|---|---|
| `none` | Already on the device | Scanning your install directory |
| `rsync` | A path or a remote machine | Listing that path, over SSH if configured |
| `script` | Whatever your script does | Running your `getlisting` script |

They are genuinely different modes rather than variations on one theme, so the sections
below cover each in turn.

### These are conveniences, not the limit

`none` and `rsync` are built in because they cover common cases without anyone writing code.
They are not the boundary of what an extension can do.

**`script` is the general case, and it has no opinion about how you get a game.** Junk Store Pro
runs your `getlisting` to find out what exists, your `downloader` to fetch one, and reads the
progress keys you print. What happens in between is entirely yours: a store's own client, a
torrent tool, `curl` against an API, `git`, a tape robot, unpacking from an archive you keep
on a NAS, or something with no network involved at all.

The only obligations are the contracts:

| You must | Documented in |
|---|---|
| Print one game identifier per line from `getlisting` | [Custom scripts](custom-scripts.md#listing-and-metadata) |
| Put the game at the install path you were handed | [Custom scripts](custom-scripts.md#downloading-and-installing) |
| Print progress keys as you go, and `Status:completed` at the end | [Downloader protocol](downloader-protocol.md) |

Satisfy those and the interface behaves exactly as it does for a shipped store: the same
grid, the same progress bar, the same install and uninstall buttons. Junk Store Pro never
inspects *how* the bytes arrived.

The same is true elsewhere. The shipped launcher scriptlets, the Generator editors, the config
sections: each is a worked answer to a common problem rather than a fence. Where this guide
describes something as "the way it works", that usually means "the way the shipped
extensions do it", and the underlying contract is narrower than the convention built on top
of it.

So if none of the three methods fits, that is not a dead end. It means you want `script`.

## none

**Nothing is downloaded.** The games are already where they need to be, and Junk Store Pro just
finds and launches them.

The listing is built by scanning your install directory for files matching **ROMs
Extension**, and using the filenames as the games. So the folder is the library.

Use this when:

- Your ROMs or games are already on the device or an SD card.
- You copy new games in yourself and want them to appear.

This is the simplest option and the right default for a personal emulator library. The
wizard chooses it when you say your ROMs are already on the device.

There is no downloader script involved, so there is nothing to write.

## rsync

**Games are copied from a path, optionally on another machine over SSH.**

The listing is built by listing that path for files matching your download extension, then
stripping the extension to get the game names. If **Use SSH** is enabled the listing and the
copy both happen over SSH; otherwise both run against a local path.

**With SSH off, the source is any path the device can reach.** Junk Store Pro runs `find` and
`rsync` against it directly, so an SD card, a USB drive, a dock, or a network share the
system has already mounted all work the same way. There is nothing remote-specific about
`rsync` here; it is being used for its copying and resume behaviour rather than for
networking.

Junk Store Pro does not mount anything itself. If the path is not currently mounted, the listing
comes back empty and installs fail. For media that is not always attached, an action's
`script-pre` and `script-post` can mount and unmount around the operation; see
[Mounting the source yourself](../guides/emulators-and-roms.md#mounting-the-source-yourself).

Settings it uses, all in the RSYNC section:

| Setting | Purpose |
|---|---|
| Use SSH | Whether to reach the source over SSH at all |
| SSH User | Username on the remote machine |
| SSH Host | Address of the remote machine |
| ROMs Path | Where the games are, on the server if using SSH |

Use this when:

- You keep a library on a NAS, desktop, or home server and want to install to the Deck on
  demand.
- The source is a mounted drive you would rather not fill the Deck from permanently.

**SSH must already work.** Junk Store Pro does not set up keys for you. Public key
authentication needs to be working before this method will list anything, and the listing
step uses a short connection timeout, so an unreachable host produces an empty list rather
than an error.

Nothing to write here either; rsync does the transfer.

## script

**Your own script fetches the game.** This is the escape hatch for anything the other two
cannot express: a storefront with a client, an API, an archive that needs unpacking.

Two scripts do the work:

- **`getlisting`** produces the games list, one per line.
- **`downloader`** fetches one game.

Both receive your configuration as environment variables, so they can read paths, hosts,
and credentials from settings rather than having them hardcoded. See
[Settings and environment variables](../concepts/config-layering.md).

The downloader is expected to report progress as it goes, using the key and value protocol
documented in [Downloader protocol](downloader-protocol.md). That is what
drives the progress bar.

Use this when:

- The source needs a client or an API call rather than a file copy.
- You need to unpack or transform what you fetched.
- Neither `none` nor `rsync` fits.

This is what the shipped Epic, Amazon, GOG, and Itch extensions use, so they are the
reference for how a real one looks.

## Choosing between them

A rough decision path:

1. **Are the games already on the device?** Use `none`.
2. **Can you get them with a plain file copy from a path or a server?** Use `rsync`.
3. **Anything else.** Use `script`, and write a `downloader`.

Start at the top. Each step down is more work, and `none` covers more cases than people
expect.

## Changing method later

The method is a setting, so you can change it, but be aware it changes how the listing is
built. Switching from `none` to `rsync` means the games list comes from the remote path
rather than your local folder, so the games you see may change. Refresh the list after
switching, and expect to fix up the paths.

Remember to regenerate the extension after changing it. See
[the regenerate step](../guides/quickstart.md#the-one-step-people-forget-regenerate).

## Import is separate

Importing a game from a local or remote source is its own path, not one of the three
methods above. It runs regardless of which method the extension uses, and is offered when
the extension's `supports-import` script says it is available. See
[Custom scripts](custom-scripts.md).

## A note on other methods

You may see references to a `wget` download method. It was planned as a fourth method and
deliberately not finished, because `script` turned out to cover it: a script can call `wget`
itself, and gets full control and working progress reporting in the process. A built in method
would have bought nothing that a short downloader does not already do.

So it is not a gap waiting to be filled. **Use `script` to fetch over HTTP.** There is a ready
made `wget_parser` in junklib that reads `wget`'s progress output for you, described in
[Using junklib for progress](downloader-protocol.md#using-junklib-for-progress).

**The `WGET` settings section is a different matter, and it is not dead.** It survived the
method being dropped, it is in use by real extensions, and it is available to yours. A
`script` downloader reads `WGET_BASE_URL` like any other setting and fetches from it however
it likes. See [WGET](settings.md#wget).

This is worth understanding as an example of where the boundary sits. The three methods exist
because they need no code at all. Anything beyond them is `script`, and `script` is not a
lesser path.

## Related

- The settings each method uses: [Settings reference](settings.md)
- Writing a downloader: [Downloader protocol](downloader-protocol.md)
- Getting ROMs discovered: [Emulators and ROM discovery](../guides/emulators-and-roms.md)
