# Troubleshooting

This section is about **extensions not behaving as you intended**: a change that had no effect,
a script that does not run, an extension that does not appear.

If instead a **game will not start**, that is a different problem needing a different method.
See [When a game will not run](guides/when-a-game-will-not-run.md).

If a word here is unfamiliar, the [glossary](../glossary.md) explains the vocabulary in
plain language.

## Nothing happened and there is no error

**Known issue: several things fail without reporting anything.** Your entry is stored, the
editor shows it, generation reports success, and no file appears or no value takes effect.
Nothing is written to a log.

This is the single most common way to lose an hour, so the list is worth knowing. Work down
it when something that should have happened did not.

| Symptom | Likely cause |
|---|---|
| A custom script is in the database but no file is written | The entry has no **`filename`**, or its **name is not one Junk Store recognises**. See below |
| A commandmap override runs the stock behaviour | The `script` body **failed to parse** and the default was written instead |
| A setting imported from a preset has no effect | **Download method or Data source.** The generated tab config is preserved and wins. See [Settings](reference/settings.md#download-method-and-data-source-set-them-in-two-places) |
| A tab populates nothing and `listing.txt` is 0 bytes | Usually the above: the extension is still on a download method you did not intend |
| An extension works for you but not for whoever you shared it with | Download method or Data source were set in the tab config UI only, so they are not in the export |
| Everything looks installed, or nothing does | The `steamclientid` column is what the interface reads. See [Items that are not games](guides/non-launchable-items.md#install-state-is-steamclientid) |

### A custom script that is never written

Two different causes produce an identical result, and neither reports anything:

**The entry has no `filename`.** That field decides what gets written. It is not defaulted
from the entry's name, so a hand-made entry without it produces nothing even with
`generate` on and a script body present. Shipped extensions all carry it, which is why the
requirement is easy to miss. **Check this first.**

**The name is not one Junk Store recognises.** Generation only writes files for the fixed
set of known script names. An entry named something of your own is stored, shown in the
editor, and never written, whether `filename` is set or not.

**`userlib` is the one slot for your own code.** If you need a helper script, that is where
it goes. See [Custom scripts](reference/custom-scripts.md).

### A commandmap script that is silently replaced

**A `script` body that is not valid shell is discarded, and the default body is generated
in its place.** The value stays in the database and stays visible in the editor, so the
action behaves as though the override was never written.

A single stray line is enough to drop the whole script.

If an override is being ignored and the path and spelling are right, compare the stored
value against the generated file. If the generated file holds the stock one-liner, the body
did not parse.

## My change did not do anything

This is the most common problem, and it usually has one of two causes.

**You did not regenerate.** Junk Store Pro generates the scripts it runs from the
Generator database. Editing a setting, or editing a script and stopping there, does
not change what runs.

Fix: regenerate the extension you changed. Keep it to that one extension rather than
rebuilding everything, since a global rebuild can overwrite unimported edits in other
extensions.

**You edited a script but did not import it first.** The Generator regenerates from
its database, not from your files. If you edited a script and then regenerated, your
edit was overwritten by whatever the database still held. This is especially easy to
hit when you edit in an external editor such as VS Code, since nothing in Junk Store Pro
knows those files changed.

Fix, in this order:

1. **Save scripts back to DB** for the extension you are working on, which imports
   your edited files.
2. Regenerate with **Regenerate installed extensions**.

Doing these the wrong way round loses the edit, and there is no undo. If it has already
happened, check whether you have a copy before redoing the work.

Keep both steps scoped to the extension you are working on. The "all extensions"
variants sweep up every extension, so they can overwrite unimported edits in ones you
were not even working on.

**You edited store.sh directly.** `store.sh` is generated. Any hand edit to it is
lost on the next regenerate. Put your change in an
[override](guides/overriding-actions.md) instead, or in one of the scripts `store.sh`
calls.

## My override is not being picked up

Check the path and the store name spelling. It has to be exactly:

```
~/.config/junkstore/overrides/<Store>/store.sh
```

`<Store>` matches the store name Junk Store Pro uses, such as `Epic`, `Gog`, `Amazon`,
`Itch`. Confirm the store's own script is looking for it:

```bash
tail -5 ~/.local/share/junkstore/scripts/Extensions/Epic/store.sh
```

You should see the `if [[ -f ... ]]` block naming your path.

Then check your function name matches the one you meant to replace:

```bash
grep '^function' ~/.local/share/junkstore/scripts/Extensions/Epic/store.sh
```

Action functions are `<Store>_<action>`, so `Epic_install`, not `install`.

If you are trying to override launching, that is not possible through this file.
Launching runs through `launcher.sh`, which does not source your overrides. See
[Overriding actions](guides/overriding-actions.md#launching-is-not-overridable-here).

Finally, check your file is valid shell. A syntax error means the whole override
fails to load, usually silently:

```bash
bash -n ~/.config/junkstore/overrides/Epic/store.sh
```

## Database is locked

Each store has its own SQLite database, and several processes reach for it at once: the
interface, your scripts, the download queue, and any refresh in flight. **Ordinary
contention is handled.** Writers queue rather than failing, so a brief overlap costs a short
wait and nothing more.

**So a lock error means sustained pressure, not an unlucky collision.** Something is writing
much more often than the design expects, and it is nearly always an extension doing it.

**The usual causes, in the order worth checking:**

**A refresh triggered from a code path that runs often.** A full refresh writes one row per
item. Firing it from something that happens repeatedly, such as a list-empty check, turns a
single expensive operation into a continuous one. This is the most common cause and the
easiest to introduce by accident.

**Per-item work at scale.** A refresh spawns one `getgameinfo` process per item, and
rendering a list spawns one process per row for its menu. At a few dozen games that is
invisible. At several hundred it is a sustained load, and anything writing underneath it
will contend.

**Polling.** A script that checks state in a loop, rather than waiting to be called, adds
pressure for as long as it runs.

**What to do:**

- **Find what is writing repeatedly**, rather than trying to make the writes faster. The
  fix is almost always removing a refresh, not optimising one.
- **Cache expensive work** in `getgameinfo`. It runs once per item, so a directory walk or
  a size calculation inside it is multiplied by the list size.
- **Do not refresh on a condition that recurs.** Refresh on an explicit user action, or once
  when a tab has genuinely never been populated.

**A caution about copying shipped extensions.** The Itch extension's `GetGames` override
fires a full refresh whenever the list comes back empty, which populates a new tab on first
open. Copied into an extension with a few hundred items it produces a full refresh and a
full set of row writes landing underneath whatever else is reading, and it is a direct cause
of lock errors. Take the pattern only if your list is small.

## Reading the logs

You do not need Desktop Mode or a terminal for this. **Use Junk Store Pro's own file
manager**, which will open a log in its text viewer.

1. Open the file manager.
2. Browse to `~/.config/junkstore/logs/`.
3. Select the log and view it.

That is the quickest route on a Deck, and it works from Gaming Mode with the controller.

### Which log to read

| File | Contents |
|---|---|
| `junk-store.log` | The store binary, where most action output lands |
| `junk-loader.log` | The loader service |
| `epic.log`, `gog.log`, and similar | Per store client logs |

Rotated copies are kept with a date suffix, for example
`junk-store.log.20260726`.

**Launch problems log somewhere else.** When a game fails to start, the useful log is
`launcher.log` inside the game's own directory, not the store log. Browse to the game's
install directory in the file manager and open it there.

That file records the resolved game path, the arguments, dependency installation, and the
final command, which is usually enough to see why a launch failed. Because the Steam
shortcut runs the launcher directly, it is written whether or not Junk Store Pro was open.

### From a terminal instead

If you are already in Desktop Mode or connected over SSH, the usual tools work:

```bash
tail -f ~/.config/junkstore/logs/junk-store.log
tail -50 /path/to/game/launcher.log
```

Following a file live is the one thing the file manager will not do, so use `tail -f` when
you want to watch an action as you trigger it.

The loader also logs to the systemd journal:

```bash
journalctl --user -u junk-loader.service -f
```

## My store tab did not appear

1. Confirm the extension exists in the runtime tree:

   ```bash
   ls ~/.local/share/junkstore/scripts/Extensions/
   ```

2. If the directory is there but the tab is not, regenerate.

3. If it is still missing, check `junk-store.log` for an error while loading the
   extension. A malformed `static.json` or a `store.sh` that fails to source will
   prevent the store from registering.

## An action runs but the UI shows nothing, or shows an error

Actions report back by printing JSON on stdout. If the JSON is malformed, or if
your script prints anything else before it, Junk Store Pro cannot read the result.

Run the script by hand to see exactly what it prints:

```bash
cd ~/.local/share/junkstore/scripts/Extensions/MyStore
./your-script
```

Watch for stray `echo` lines, progress output, or debug text going to stdout.
Anything diagnostic should go to stderr instead:

```bash
echo "debug info" >&2
```

See [Action results](reference/actions-and-types.md#action-results) for the expected shapes.

## Process exited with code 127

**127 means "not found", and two different things produce it.** Having found one, it is easy
to fix something that was never in the failing path, because the error does not change.

**The extension has no `downloader` script.** This is the usual cause when the message comes
from the download queue. The queue's row carries `game_id`, `path` and `mode`, which mirror
`downloader`'s three arguments exactly, so a row that looks correct alongside a 127 points
at the script being absent rather than at its arguments being wrong.

**The interpreter is not on PATH.** See below. A `#!/usr/bin/env python3` shebang that works
when the script is called directly can still fail from a commandmap body.

## An action cannot find python3, or another interpreter

**Known issue: actions run with a PATH that does not include `/usr/bin`.** A commandmap body
calling `python3` exits 127, while the same shebang in a script Junk Store invokes directly,
such as `getlisting` or `getgameinfo`, works.

The inconsistency between the two contexts is the surprising part, and it is worth knowing
before you spend time on the script itself.

**Do not rely on PATH in a commandmap body.** Use an absolute interpreter path, with a
lookup as a fallback:

```bash
PY="$(command -v python3 || echo /usr/bin/python3)"
"$PY" "$SCRIPT"
```

## I typed a value into a field and now it is broken

Pressing Y on a field lets you type a value directly, which bypasses the validation
the normal control would apply. A malformed value reaches the scripts exactly as you
typed it.

Press **Menu** on that field to reset it to its default. Then regenerate.

If you are not sure which field you changed, the settings reference lists the default
for every field. See [Settings reference](reference/settings.md).

## Testing a script safely

Scripts are ordinary shell, so check them before wiring them up:

```bash
bash -n script-name     # syntax only, does not run it
bash -x script-name     # run with a trace of each command
```

## I lost my extension

The extension directory is in your home directory and is not version controlled by
default, so there is no automatic backup.

If the extension is still in the Generator database, run **Regenerate installed
extensions** to get the scripts back.

If you made the directory a git repository, recover from there instead:

```bash
cd ~/.local/share/junkstore/scripts/Extensions/MyStore
git status          # what changed
git checkout .      # discard changes, back to last commit
```

If you have a committed export, import it back and regenerate:

```bash
$HOME/.local/share/junkstore/junk-store Generator importpresetfile /path/to/repo MyStore
```

That restores the definition as well as the scripts, so it is the more complete recovery.
See [Export, import, source control](reference/sharing-and-licensing.md).

If the database entry is gone and there is neither git history nor an export, the
extension cannot be recovered. That is the argument for committing an export before you
start work. See
[Put your extension in git](guides/authoring-by-hand.md#put-your-extension-in-git).

## Starting over on one extension

Delete the extension in the Generator (**Delete Extension**), then restore it and
regenerate. This is cleaner than trying to unpick a half edited extension.

What you restore from depends on where it came from:

- **A shipped extension:** download it again with **Download preset from server**.
- **Your own extension:** import your last committed export with `importpresetfile`. See
  [Export, import, source control](reference/sharing-and-licensing.md).

**Deleting is not recoverable without one of those.** If you have neither, export the
extension before you delete it.

## Getting help

When reporting a problem, the useful details are:

- What you changed, and which level you changed it at (setting, override, or
  script).
- Whether you saved scripts back to the database and regenerated.
- The relevant lines from `~/.config/junkstore/logs/junk-store.log`.
- The output of running the script by hand, if it is a script problem.
