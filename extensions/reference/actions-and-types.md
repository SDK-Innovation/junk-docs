# Actions, results, and types

Lookup tables for action names, the JSON shapes actions return, action types, and config
field types. For how any of it fits together, see the concepts sections.

## Paths

| Path | What it is |
|---|---|
| `~/.local/share/junkstore/scripts/Extensions/<Store>/` | The scripts Junk Store runs, and what the Generator imports from |
| `~/.config/junkstore/overrides/<Store>/store.sh` | Your personal action overrides |
| `~/.config/junkstore/databases/generator.db` | The Generator database, source of truth for regeneration |
| `~/.config/junkstore/` | Settings and databases generally |

Junk Store does not use any other location. References to `homebrew` in older
notes or internal strings are historical.

## Actions

Action functions in a generated store script are named `<Store>_<action>`, for
example `Epic_install` or `Itch_getgames`. The registered action names for a store are
listed in the `ACTIONS` array at the end of its `store.sh`.

To see the exact list for a store on your machine:

```bash
grep '^function' ~/.local/share/junkstore/scripts/Extensions/Epic/store.sh
```

### Actions every extension gets

| Action | Purpose |
|---|---|
| `GetGames` | Return the game list shown in the grid |
| `Init` | Initialise the game set |
| `refresh` | Refresh the games list |
| `clearallcache` | Clear cached data |
| `deleteunlinkedgames` | Remove entries with no matching install |
| `GetGameDir` | The install directory for a game |
| `GetSteamClientId` | The Steam shortcut ID, empty when not installed |
| `ImportGame` | Import a game from a local or remote source |
| `SupportsImport` | Whether import is available for this store |
| `UpdateConfigValue` | Change a single config value |
| `GetTabShellEnvironment` | Tab settings exposed as shell variables |
| `GetGameShellEnvironment` | Game settings exposed as shell variables |
| `GetDynamicShellEnvironment` | Dynamic config as shell variables |
| `DeleteGameFromExtension` | Remove a game from the database |

### Actions that appear based on configuration

| Setting | Value | What it adds |
|---|---|---|
| `needs-login` | true | Login and logout actions |
| `platform` | `Proton` or `Linux` | Proton related actions |
| `has-bat-files` | true | Actions to read and write the game's stored `.bat` files |
| `data-source` | `Epic` | Epic specific actions |

Commonly seen action names on shipped stores include `install`, `uninstall`,
`verify`, `update`, `download`, `getdetails`, `getgames`, `getexelist`,
`savesetting`, `savetabconfig`, `runlauncher`, and `supportsimport`.

`verify` and `update` need no scripts of their own. They run the same `downloader` with a
different mode, described in
[The third argument is a mode](downloader-protocol.md#the-third-argument-is-a-mode).

There is no `launch` action. Starting a game is handled by `launcher.sh` and the
per platform scriptlets in `launchers/`, not by an action in `store.sh`. The
`runlauncher` action is the entry point into that path.

## Action results

Scripts talk to Junk Store by printing JSON on stdout. Two shapes you will use
most:

**Success**

```json
{"Type": "Success", "Content": {"Message": "Done"}}
```

**Error**

```json
{"Type": "Error", "Content": {"Message": "Something went wrong"}}
```

Written in shell, with the escaping you need inside a double quoted string:

```bash
echo "{\"Type\": \"Success\", \"Content\": {\"Message\": \"EOS overlay Enabled\"}}"
```

If an action has nothing to report, printing nothing is acceptable.

Other `Type` values exist for structured content, for example `GameGrid` for a
game list, `GameDetails`, `GameImages`, `GameSize`, `Status`, and the various
editor types. The simplest way to get these right is to read the corresponding
script in a shipped extension and match its output.

### How long a result stays on screen

**The two types differ in more than wording**, which is worth knowing before deciding which
to return:

| Type | Shown as | Stays? |
|---|---|---|
| `Success` | A toast | No. It fades, and is easily missed |
| `Error` | A dialog | Yes, until dismissed |

**Known issue: there is no advisory type between them.** Anything the user has to read has
to be returned as an `Error` to stay on screen, which means a deliberate refusal renders
under *Something went wrong*.

A safety check such as "this version is used by 2 games" therefore reads as a fault. Until
a third type exists, an error dialog with carefully chosen wording is usually the lesser of
the two, since a toast the user misses is worse than one that overstates its severity.

**`getdetails` is not rendered when the tab is a list.** It returns a `Description`, and
that only reaches the screen for a grid. Overriding the action is wasted work on a
list-rendered tab.

### What a list row receives

Each item in a game list arrives with six fields, and nothing else:

```
ID, SteamClientID, Publisher, Images, ShortName, Name
```

That decides what you can put in front of someone while they browse:

| Field | Rendered? | Use |
|---|---|---|
| `Name` | Yes | The only place to surface per-item state |
| `Publisher` | Yes, at the right of the row | The second visible field. A natural home for a size, a date or a source on anything that is not a game |
| `Images` | Yes | The only visual channel |
| `ID`, `ShortName`, `SteamClientID` | No | Identity and install state |

**Rows cannot be coloured or styled.** There is no status, class or style field, so any
design that depends on marking rows visually needs rethinking before you start.

**`notes` never reaches the list**, and neither does anything else you emit. Keys outside
the documented set are dropped.

### `SteamClientID` is what "installed" means

**The interface treats an item as installed when its `steamclientid` column has a value.**
That drives the installed filter and the per-row controls.

The install lifecycle normally writes it. An extension that installs its own items never
goes through that lifecycle, so it has to maintain the column itself. See
[Items that are not games](../guides/non-launchable-items.md#install-state-is-steamclientid).

## Action types

When an action is registered in the Generator it has a *type*, which mostly declares what
kind of content the action returns. The ones you are most likely to meet:

| Type | Meaning |
|---|---|
| `Shell` | Returns shell variable assignments |
| `GameGrid` | Returns the game list for the grid |
| `GameDetails` | Returns detail page content |
| `Executable` | Runs an executable |
| `IniEditor` | Presents an ini style config editor |
| `ImageEditor` | Presents the artwork editor |
| `Init` | Runs at initialisation |
| `ScriptActions` | Supplies a set of script actions |
| `TabPage` | Supplies tab page content |

Two caveats, because the field does not behave uniformly:

- **`Init`, `ScriptActions`, and `TabPage` change what runs.** Those three generate a call
  to the JSON helper rather than to the store dispatcher, so do not use them unless that is
  what you want.
- **`ScriptAction` and `ScriptActionConfirm` are not yours to set.** For script actions the
  type is derived from the `confirm` field, not from `type`. Set `confirm` to get a
  confirmation prompt.

See [What `type` actually does](../concepts/the-generator.md#what-type-actually-does) for the
detail.

## Config field types

Config fields declared by an extension render as form controls:

| Type | Control |
|---|---|
| `String` | Text box |
| `Boolean` | Toggle |
| `Number` | Numeric input |
| `Range` | Slider, using the field's minimum and maximum |
| `Enum` | Dropdown of fixed choices |
| `File` | File picker |
| `Directory` | Directory picker |
| `Binary` | Binary value |

For what each individual setting in the shipped config sections does, see
[Settings reference](settings.md). For the structure these fields live in,
see [The config schema format](../concepts/config-schema.md).

## The four Generator editors

The Generator exposes four editors, each covering one part of an extension's
definition:

| Editor | What it controls |
|---|---|
| `commandmap` | Which actions exist and what each one calls |
| `customscripts` | Your custom script entries |
| `launchers` | Per platform launcher scriptlets |
| `settingsfile` | The contents of the settings file |

## Generator operations

Found in the Generator tab:

| Operation | What it does |
|---|---|
| Generate all extensions | Rebuild scripts for every extension from the database |
| Regenerate installed extensions | Rebuild only installed extensions, faster |
| Save scripts back to DB | Import scripts from the runtime tree into the database |
| Save all scripts back to DB | The same, across all extensions |
| Import the preset from a file | Load an extension from a `.json` file. Done from the command line, see below |
| Export the preset to a file | Save an extension to a `.json` file. Done from the command line, see below |
| Download preset from server | Fetch one Junk Store extension |
| Download all presets from server | Fetch all Junk Store extensions |
| Delete Extension | Remove an extension |
| Add Game | Add a single game entry. Reached through the file manager rather than a form, see below |
| Extension wizard | Create a new extension from answers to a few questions |

**On adding games:** there is no general form for entering a game by hand. The supported
route is the file manager's **Add to Steam**, which creates the game entry and its Steam
shortcut from the file you selected. A `.exe` additionally gets its launcher set to `Proton`,
with the executable, its directory and the install path recorded, so it is ready to run.
Normally an extension finds its own games from the location you configured, so adding entries
individually is the exception, not the workflow.

## Sharing an extension

An extension exports to a single `.json` file, which is what you share, back up, and
commit to version control.

**This applies to extensions you created.** The shipped Epic, Amazon, GOG, and Itch
extensions are source available, not open source, and may not be redistributed. An export
is a complete copy of everything in the extension, so exporting one of them and passing on
the file redistributes their code just as surely as copying the scripts would. Back them up
for your own use if you like; do not publish or pass on the result. See
[What you may and may not share](sharing-and-licensing.md#what-you-may-and-may-not-share).

**Import and export are command line operations.** The Generator menu lists "Import the
preset from a file" and "Export the preset to a file", but the working route is the command
line, which takes the directory and name as arguments.

For export that is merely a detail. For import it is a deliberate speed bump. Importing an
extension runs its code, so the friction is doing useful work: it means whoever imports has a
terminal open, has the file on disk, and typed the extension's name. A menu item invites
tapping a thing somebody linked. Same operation, very different amount of thought in front of
it.

```bash
JS="$HOME/.local/share/junkstore/junk-store Generator"

$JS importscripts MyStore              # edited scripts -> database
$JS exportpresetfile /path/to/dir MyStore   # database -> MyStore.json
$JS importpresetfile /path/to/dir MyStore   # MyStore.json -> database
```

Run `importscripts` before exporting, or you export the database's older copy of your
scripts rather than the ones you edited.

**Download preset from server** in the menu fetches extensions published by the Junk
Store project.

**`importpresetfile` runs somebody else's code.** An extension contains shell and Python
scripts that Junk Store executes as you, unsandboxed, and some of them run simply because the
extension is present. Only import from a source you trust, and read the scripts first if you
are unsure. See
[Only import extensions from people you trust](sharing-and-licensing.md#only-import-extensions-from-people-you-trust).

For the full workflow, including keeping the exported file in git, see
[Sharing and licensing](sharing-and-licensing.md).

Note this versions the scripts, not the Generator definition, so it is not a complete
snapshot of the extension.

## Progress reporting

Long running operations such as downloads report progress back to the UI. Rather
than reproducing a format here that may differ per store, copy the approach from
the `downloader` script of a shipped extension close to your use case, since that
is the code the UI is known to work with.
