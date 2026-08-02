# Troubleshooting

This section is about **extensions not behaving as you intended**: a change that had no effect,
a script that does not run, an extension that does not appear.

If instead a **game will not start**, that is a different problem needing a different method.
See [When a game will not run](guides/when-a-game-will-not-run.md).

If a word here is unfamiliar, the [glossary](../glossary.md) explains the vocabulary in
plain language.

## My change did not do anything

This is the most common problem, and it usually has one of two causes.

**You did not regenerate.** Junk Store generates the scripts it runs from the
Generator database. Editing a setting, or editing a script and stopping there, does
not change what runs.

Fix: regenerate the extension you changed. Keep it to that one extension rather than
rebuilding everything, since a global rebuild can overwrite unimported edits in other
extensions.

**You edited a script but did not import it first.** The Generator regenerates from
its database, not from your files. If you edited a script and then regenerated, your
edit was overwritten by whatever the database still held. This is especially easy to
hit when you edit in an external editor such as VS Code, since nothing in Junk Store
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

`<Store>` matches the store name Junk Store uses, such as `Epic`, `Gog`, `Amazon`,
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

## Reading the logs

You do not need Desktop Mode or a terminal for this. **Use Junk Store's own file
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
shortcut runs the launcher directly, it is written whether or not Junk Store was open.

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
your script prints anything else before it, Junk Store cannot read the result.

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
