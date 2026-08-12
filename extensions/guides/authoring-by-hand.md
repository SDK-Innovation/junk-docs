# Authoring an extension by hand

This is for when the settings and overrides cannot express what you need: a
storefront with its own login, a custom downloader, or install logic that does not
fit the standard shape.

You will be writing shell scripts. You do not need to build anything or install
development tools.

## The model in one paragraph

An extension is a directory of shell scripts plus a definition held in Junk
Store Pro's Generator database. The Generator *generates* the top level `store.sh`
from that definition, wiring up the action functions the UI calls. Your job is to
supply the scripts that do the real work, register them in the Generator, and
regenerate.

## Two trees, and which one matters

```
~/.local/share/junkstore/scripts/Extensions/<Store>/
    The runtime tree. This is what Junk Store Pro executes.
    This is also what the Generator imports from.

~/.config/junkstore/databases/generator.db
    The Generator database. The source of truth for regeneration.
```

The round trip is:

1. Edit a script in the runtime tree.
2. **Save scripts back to DB**, which imports your edited files into the database.
3. **Regenerate**, which writes the scripts back out from the database.

Skipping step 2 or 3 is the most common reason a change appears to do nothing.

### Order matters, and getting it wrong loses your work

Generation writes **from the database to your files**. So if you edit a script outside
Junk Store Pro, in a text editor such as VS Code, and then regenerate without importing
first, **the database version overwrites your edits and they are gone.**

This is the single easiest way to lose work in this workflow. Whenever you have edited
files outside Junk Store Pro:

```
Save scripts back to DB    <- first, always
Regenerate                 <- only after the import
```

If you are unsure whether your edits made it into the database, copy the files
somewhere safe before you regenerate. There is no undo.

### Work on one extension at a time

Prefer the per extension operations over the global ones:

- **Save scripts back to DB** imports the extension you are working on. **Save all
  scripts back to DB** does every extension.
- Regenerate just what you are working on rather than rebuilding everything.

This matters for the same reason as above. A global operation sweeps up every
extension, including ones with edits you had not imported yet, so a single careless
"do everything" click can overwrite work in an extension you were not even thinking
about. Keeping the scope to the extension in front of you keeps the blast radius
small.

## Always start with the wizard

Use the Generator's extension wizard to create the extension, then edit what it
produced. See
[Quick start](quickstart.md#a-create-a-new-extension-with-the-wizard).

**Do not copy an existing extension's directory.** It looks like a shortcut and it is
the opposite. Junk Store Pro is convention driven: the store name appears in the directory
name, in `PLATFORMS`, in `STORE_NAME`, in the name of every action function
(`<Store>_<action>`), and in the Generator database entry that ties it all together. A
copied directory means renaming all of that consistently, and anything you miss fails
quietly rather than with a useful error. The wizard writes every one of those from the
name you give it.

So: wizard first, then hand edit. What follows is about the editing.

## What the wizard gives you

A generated extension contains roughly these files. Knowing which is which tells you
where to make a change:

```
MyStore/
    store.sh              generated, do not hand edit
    settings.sh           environment setup, sourced first
    static.json           static metadata
    launcher.sh           how a game gets launched
    launchers/            per platform launcher scriptlets
    downloader            fetches the game
    gamesize              reports install size
    get-launch-options    launch options offered in the UI
    install_deps.sh       installs the tools this extension needs on the host
    junklib.py            shared python helpers
```

Simple extensions have only what they need, so do not expect every file in every
extension.

Then work through the files, replacing the parts specific to the original.

## The files you will actually edit

**`settings.sh`** is sourced before anything else. Use it to export variables the
rest of your scripts need. The shipped versions work out where the SD card is mounted
and export `SD_PATH`, which gives you the idea.

**`launcher.sh`** is what the Steam shortcut for an installed game runs, so it is the
entry point for actually playing anything. It works like this:

1. It exports the runtime environment variables and sources `settings.sh`.
2. It fetches the tab and game settings by calling the binary's
   `TabShellEnvironment` and `GameShellEnvironment` actions, and evaluates the
   shell assignments they return. This is how your config values become variables.
3. It looks up the game directory.
4. It switches on the platform and sources the matching scriptlet from
   `launchers/`, for example `Proton`, `Linux`, `Dosbox`, `RetroArch`, `ScummVM`.

**You will almost certainly not need to edit `launcher.sh`.** Extensions hardly ever
touch it, and it is stable in what it does: the same setup and dispatch for everyone.
Treat it as plumbing.

**`launchers/`** is where the custom work goes. One scriptlet per platform, and a game
picks its scriptlet through the `platform` setting. This is the file to change when you
need launch behaviour that settings cannot express.

The scriptlets do the real work and can be substantial. The shipped `Proton` one reads
dozens of runtime settings (esync, fsync, FSR, frame limiting, anti cheat runtimes, extra
arguments), resolves the game path and compatibility id, runs dependency installation on
first launch, and finally evaluates the command. If you are writing a scriptlet for a new
emulator, start from the closest existing one rather than from nothing.

**`downloader`** fetches a game. It is expected to report progress as it goes. See
[Progress reporting](../reference/actions-and-types.md#progress-reporting).

**`gamesize`** prints how much space an install takes, used by the UI.

**`static.json`** is what puts the extension on screen: its tab, where it is grouped, and the
action sets the interface can invoke. Without it the scripts still run when something calls
them, but nothing appears. See [static.json](../reference/static-json.md).

**Do not hand edit `store.sh`.** It is generated and your changes will be
overwritten on the next regenerate. Everything in it comes from the Generator
definition.

## What the generated store.sh gives you

It is worth understanding what you get for free. The generated `store.sh`:

- Sources your `settings.sh`.
- Registers your store into `PLATFORMS` and exports `STORE_NAME`.
- Defines an action function per registered action, named `<Store>_<action>`, each
  of which typically calls the `junk-store` binary or one of your scripts.
- Populates the `ACTIONS` array the UI reads to build its buttons.
- Sources your override file last, if you have one.

So the actions the UI offers come from the Generator definition, not from your
script files directly. Adding a script is not enough on its own; the action has to
be registered.

## Actions you get by default

Every extension gets a mandatory set, which includes:

| Action | Purpose |
|---|---|
| `GetGames` | Return the game list for the grid |
| `Init` | Initialise the game set |
| `refresh` | Refresh the games list |
| `clearallcache` | Clear cached data |
| `deleteunlinkedgames` | Remove entries with no matching install |
| `GetGameDir` | Where a game is installed |
| `GetSteamClientId` | The Steam shortcut ID, empty if not installed |
| `ImportGame` | Import from a local or remote source |
| `SupportsImport` | Whether import is available |
| `UpdateConfigValue` | Change one config value |

Further groups are switched on by configuration:

- Setting `needs-login` adds the login and logout actions.
- Setting `platform` to `Proton` or `Linux` adds the Proton actions.
- Setting `has-bat-files` adds the actions for editing a game's stored `.bat` files.
- Setting `data-source` to `Epic` adds the Epic specific actions.

See the [action reference](../reference/actions-and-types.md#actions) for the full picture.

## Registering your scripts with the Generator

Once your scripts are in place in the runtime tree:

1. Open the Generator tab.
2. Choose **Save scripts back to DB** for the extension you are working on. This
   imports your edited scripts into the Generator database.
3. Regenerate with **Regenerate installed extensions**.

Do the import first, every time. Regenerating before importing overwrites your edited
files with whatever the database still holds. Keep both steps scoped to the one
extension rather than using the "all extensions" variants.

If you added or changed actions rather than just script bodies, you will also want
to check the editors in the Generator UI. There are four:

- **commandmap**, which actions exist and what they call
- **customscripts**, your custom script entries
- **launchers**, the per platform launcher scriptlets
- **settingsfile**, the settings file contents

These are how you change the definition itself rather than just the script bodies.
Every field in all four is documented in
[Generator settings](../concepts/the-generator.md), including what the generated
function ends up looking like.

## Testing as you go

Scripts are ordinary shell, so you can run them directly on the Deck to check them
before involving the UI:

```bash
cd ~/.local/share/junkstore/scripts/Extensions/MyStore
bash -n store.sh          # syntax check
./downloader --help       # or whatever your script expects
```

Junk Store Pro communicates with scripts over stdout using JSON. If you run a script
by hand you will see that JSON, which is a good way to confirm you are emitting
the right shape. See [Action results](../reference/actions-and-types.md#action-results).

## Put your extension in git

The extension directory is not version controlled by default, so nothing protects your
work. Making it a git repository is the single best habit here, and it costs one
command:

```bash
cd ~/.local/share/junkstore/scripts/Extensions/MyStore
git init
git add -A
git commit -m "working extension"
```

Why this is worth doing:

- **It gives you history.** You can see what you changed and when, rather than guessing
  which edit broke the launch.
- **It undoes accidents.** The regenerate direction described above overwrites files
  from the database. If that eats an edit, `git diff` shows you exactly what was lost
  and `git checkout` brings it back.
- **You can experiment freely.** Try something drastic, and `git checkout .` puts
  everything back.

**Commit before you export, and before you regenerate.** Those are the two moments
where files get rewritten, so a commit immediately before either one means the worst
case is a `git checkout` rather than redoing the work.

```bash
git add -A && git commit -m "before regenerate"
```

Note this versions the **scripts**, not the Generator database, so it is not a complete
snapshot of the extension. It does cover the part you are actually hand editing.

A git repo here is for **history and recovery of this extension**. It is not a way to
start a new one: cloning it under a different name would leave the old store name baked
into the scripts and no database entry, which is the mess described at the top of this
page. New extensions come from the wizard.

## When something does not work

See [Troubleshooting](../troubleshooting.md). The two most common causes are
forgetting to save scripts back to the database, and forgetting to regenerate.
