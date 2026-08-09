# Items that are not games

Every shipped extension lists games. They launch, they get Steam shortcuts, and Junk Store
owns their install state. The contracts do not require any of that, and an extension can
list anything: compatibility tools, runtimes, mods, wallpapers, anything with a name and a
download.

**But the defaults assume games.** Each assumption is opt-out rather than opt-in, so
building a non-game extension is mostly a matter of knowing which ones to turn off. None of
them is difficult. The difficulty is that getting one wrong tends to fail quietly.

This page collects them in one place. It came out of building a working compatibility tool
manager, where roughly half the effort went on discovering which assumptions to shed.

## The six assumptions

| Assumption | What to do instead |
|---|---|
| Items launch | No launcher needed. `Exe` will be empty, and that is fine |
| Install creates a Steam shortcut | End the downloader on `cancelled`, not `completed` |
| Junk Store owns install state | Write `steamclientid` yourself when state changes |
| Junk Store places the files | Ignore the install path it hands you and put them where they belong |
| Your own helper scripts get generated | Only `userlib` does |
| The list can show status | Only through `Name`. Six fields arrive, none of them styleable |

Each is discoverable from the existing contracts. None is obvious.

## Ending on `cancelled` to avoid a Steam shortcut

**This is the most useful thing on the page.**

[The downloader protocol](../reference/downloader-protocol.md) explains that
`Status:completed` ends the download and triggers the install phase. For a game that is
what you want: the install phase adds the Steam shortcut that makes it launchable.

For something that is not launchable, that shortcut is a dead tile with an empty `Exe`.

**Ending on `Status:cancelled` instead skips the install phase entirely.** The queue,
progress bar, speed and ETA all still work, and no shortcut is created. Your files are
already in place, because your downloader put them there.

```
Status:cancelled
```

The only cost is that the queue row reads as cancelled rather than finished.

### Why this matters more than it looks

**Uninstall removes the shortcut using the game's `steamclientid`.** That works when Junk
Store owns the install, because the lifecycle sets the column.

An extension that installs its own items and never sets it hits a compounding problem:
install creates a shortcut, uninstall has nothing to remove, and a reinstall adds a second
one. Repeat that a few times and the entries accumulate with nothing in Junk Store able to
clear them.

**Two ways out**, and the first is usually better:

- **Never create the shortcut.** End on `cancelled` for something that should not be a
  library entry at all.
- **Keep `steamclientid` current**, as [below](#install-state-is-steamclientid), so uninstall
  can do its job.

For an extension whose whole purpose involves installing and removing things, that cycle is
the normal case rather than an edge, which is why it is worth deciding early.

## Install state is `steamclientid`

**The interface treats a game as installed when its `steamclientid` column has a value.**
That is what the installed filter keys off, and what the per-row controls check.

Normally the install lifecycle writes it for you. An extension that installs its own items
never goes through that lifecycle, so nothing ever looks installed:

- The installed toggle returns nothing, for items that are plainly installed.
- Returning to the tab restores the toggle's visual state while passing an empty
  `installed` argument, so the control reads as active over an unfiltered list.

**The fix is to write a value into that column yourself** whenever installed state changes.
Everything then works natively, including the restore-on-entry path, and your extension can
drop any filtering of its own.

**Emitting `installpath` from `getgameinfo` does not work.** Keys outside
[the documented set](../reference/custom-scripts.md) are dropped, so the column is the only
route.

## The interface already runs your code

**Junk Store surfaces controls of its own, and they call actions you can override.** This is
worth knowing before you add anything, because the natural assumption is that a menu entry
is how you make something reachable.

| Control | Appears | Runs |
|---|---|---|
| The per-row download button | On every row | `downloader` |
| Uninstall | For anything the interface considers installed | The uninstall action |
| Delete from Database | On the row's menu | The delete action |

**Overriding those actions' `script` is usually all that is needed.** Adding script actions
for install and remove, wiring `script-set`, `confirm` and `title` on each, generally
duplicates what is already there.

Note that Uninstall appears based on `steamclientid`, so it follows the section above: if
you are not maintaining that column, the control will not appear.

## What a list row receives

Each item in a game list arrives with six fields, and nothing else:

```
ID, SteamClientID, Publisher, Images, ShortName, Name
```

That determines what is possible, and it is worth reading before designing a layout:

- **Rows cannot be coloured or styled.** There is no status, class or style field.
- **`Publisher` is rendered**, at the right of each row. It is the second visible field per
  item, and the natural home for a size, a date or a source on anything that is not a game.
- **`notes` never reaches the list.**
- **`Name` is the only place to surface per-item state** while browsing.
- **`Images` is the only visual channel available.**

## Presenting information

**Known issue: there is currently no good way to tell the user something.** Three surfaces
that would carry it are missing or unsuitable.

**No detail page in a list-rendered tab.** `getdetails` returns a `Description`, and it is
never rendered when the tab is a list. Overriding that action is wasted work unless the tab
is a grid.

**No persistent message.** A script action's result renders as a dialog only for
`Type: Error`. `Type: Success` is a toast that fades and is easily missed.

**No advisory result.** A deliberate refusal, such as "this version is used by 2 games",
has to be returned as `Type: Error` to stay on screen, so it renders under *Something went
wrong*. A safety check reads as a fault.

**Until there is a third result type**, the options are a fading toast or an error dialog.
For anything the user must act on, an error dialog with clear wording is the lesser of the
two.

## Scale

**The cost model is one process per item.** That is invisible at a few dozen games and very
visible beyond it:

- A refresh spawns **one `getgameinfo` process per item**.
- Rendering the list spawns **one `get-json.py` per row** for its menu.

At 221 items that is 221 interpreter startups per refresh. Anything expensive inside
`getgameinfo` is multiplied by the list size: walking an install directory to report its
size cost roughly 30,000 extra `stat()` calls per refresh before it was cached.

**Do not copy the Itch `GetGames` auto-refresh pattern for a large list.** The shipped Itch
extension fires a full refresh whenever the list comes back empty, and at a few hundred
items that is a direct cause of *database is locked* errors. See
[Database is locked](../troubleshooting.md#database-is-locked) for the general case.

## Sharing a directory with other extensions

**Anything writing to a well-known location has to expect company.** Compatibility tools all
land in `compatibilitytools.d`, so an extension that lists that directory to work out what
it has installed will pick up every other tool manager's installs as well.

Two extensions in this space installed side by side will each list the other's tools unless
they track their own installs separately.

## Related

- What the downloader prints, and what each status means:
  [Downloader protocol](../reference/downloader-protocol.md)
- Which hooks exist and what they receive:
  [Custom scripts](../reference/custom-scripts.md)
- Action types and results: [Actions and types](../reference/actions-and-types.md)
- When something fails without an error:
  [Troubleshooting](../troubleshooting.md)
