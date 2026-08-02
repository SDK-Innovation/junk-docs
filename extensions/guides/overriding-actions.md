# Overriding actions

An override lets you change how one action behaves without modifying the
extension. Your change lives in its own file, so regenerating or updating the
extension will not wipe it out.

**Scope:** an override replaces an action for the whole store, so it applies to every
game in that store. It is not a per game change. If you want different behaviour for
a single game, use that game's own config instead, described in
[Settings reference](../reference/settings.md#tab-config-versus-game-config).

This is the right tool when an existing store does almost what you want. If you
need a whole new store, see [Authoring by hand](authoring-by-hand.md).

## How it works

Every generated store script ends with these lines:

```bash
if [[ -f "${HOME}/.config/junkstore/overrides/Epic/store.sh" ]]; then
    source "${HOME}/.config/junkstore/overrides/Epic/store.sh"
fi
```

Your file is sourced **last**, after all the store's own functions are defined.
Anything you define with the same name as an existing function replaces it. That
is the whole mechanism.

### What that gives you, for better or worse

Because your file is sourced after everything, **every action is interceptable**. Not a
chosen set of extension points: every function the store defines, at every stage of the
loop. Listing, download, install, launch options, uninstall, login, whatever that store has.

And for each one you can act on the way in, on the way out, or both:

```bash
eval "original_Epic_getgames() $(declare -f Epic_getgames | tail -n +2)"

function Epic_getgames() {
    export SOMETHING=1                        # before: change what the original sees
    original_Epic_getgames "$@" | your_filter # after: change what the interface sees
}
```

The interface reads whatever you print. It has no way to tell your filtered output from the
store's own, which is what makes this powerful and is also the entire risk. You can rewrite
a games list, change install paths, add entries that exist nowhere upstream, or swallow an
error the store reported.

**Nothing checks any of it.** No validation between your override and the interface, no
sandbox, and no indication anywhere that an action has been modified. An override that
prints malformed output gives you a broken screen with nothing pointing at the local file
that caused it, which is why [Testing your override](#testing-your-override) is worth doing
from a terminal before you trust it.

Worth being deliberate about scope for the same reason. Wrapping one action and leaving the
rest alone is easier to reason about, and much easier to undo, than a file that redefines
half a store.

## Where to put your file

```
~/.config/junkstore/overrides/<Store>/store.sh
```

`<Store>` is the store name as Junk Store knows it: `Epic`, `Gog`, `Amazon`,
`Itch`, or whatever your own extension is called. The directory will not exist
until you create it.

```bash
mkdir -p ~/.config/junkstore/overrides/Epic
```

## Naming the function you want to replace

Action functions are named `<Store>_<action>`. For example, in the Epic store
script you will find functions such as:

```bash
function Epic_clearallcache() { ... }
function Epic_deleteunlinkedgames() { ... }
function Epic_disable-eos-overlay() { ... }
```

To find the exact name, look at the store's generated script:

```bash
grep '^function' ~/.local/share/junkstore/scripts/Extensions/Epic/store.sh
```

The list of registered action names appears near the end of the same file, in the
`ACTIONS` array. Common ones include `install`, `uninstall`, `verify`, `update`,
`refresh`, `download`, `getgames`, `getdetails`, and `supportsimport`.

There is no `launch` action. Starting a game goes through `launcher.sh`, not
`store.sh`, which is why it cannot be overridden here. See the next section.

## Launching is not overridable here

Game launching does not go through `store.sh`, so an override cannot change it.

Launching runs through a separate script, `launcher.sh`, which is what the Steam shortcut
for an installed game actually runs. It sets up the environment and then switches on the
platform to source a scriptlet from the extension's `launchers/` directory (`Proton`,
`Linux`, `Dosbox`, `RetroArch`, `ScummVM`, and so on). `launcher.sh` does not source your
overrides file.

Note the division: `launcher.sh` is shared plumbing that extensions rarely change, and
the scriptlets in `launchers/` are the custom part. Any launch change belongs in a
scriptlet.

To change launch behaviour you have two options:

- **Adjust settings.** Most launch behaviour is driven by config. The Proton
  scriptlet alone reads a large set of runtime settings for esync, fsync, FSR,
  frame limiting, anti cheat runtimes, extra arguments, and more. Changing those in
  the tab or game config is usually what you actually want. See
  [Settings reference](../reference/settings.md).
- **Edit the launcher scriptlet.** For behaviour settings cannot express, change
  the scriptlet for that platform through the Generator's launchers editor, then
  regenerate. See
  [Generator settings](../concepts/the-generator.md#launchers-how-games-start).

Be aware of the scope before you edit. Launcher scriptlets start from a shared set
of templates, and an extension can carry its own customised copy instead. So a
change reaches either one extension or many, depending on which you edit:

- Changing the **shared template** for a platform affects every extension that is
  still using the default for it.
- Changing an **extension's own** copy affects only that extension.

Among the shipped extensions both cases exist: some use the shared Proton template
unchanged, while Epic and GOG each carry their own modified version.

Either way the change applies to all games on that platform. Note that an override
is not narrower in that sense: it replaces an action for the whole store, so it also
applies to every game. The difference is not scope within a store, it is that an
override lives in your own config and survives updates, whereas a scriptlet edit
changes the extension itself.

## Example: wrap an existing action

Say you want to export a variable before an action runs. This works for any action
that exists as a function in `store.sh`, such as `install` or `refresh`.

```bash
# ~/.config/junkstore/overrides/Epic/store.sh

# Keep a reference to the original so you can still call it.
eval "original_Epic_install() $(declare -f Epic_install | tail -n +2)"

function Epic_install() {
    export MY_TWEAK=1
    original_Epic_install "$@"
}
```

The `declare -f` trick copies the original function under a new name so your
replacement can still call it. If you do not need the original behaviour at all,
just define your own function and ignore it.

## Example: replace an action completely

```bash
# ~/.config/junkstore/overrides/Itch/store.sh

function Itch_clearallcache() {
    # Your own logic instead of the default.
    rm -rf "${HOME}/my-cache-dir"
    echo "{\"Type\": \"Success\", \"Content\": {\"Message\": \"Cache cleared\"}}"
}
```

## What your script can rely on

By the time your override is sourced:

- `STORE_NAME` is exported and set to the store name.
- The store's `settings.sh` has been sourced, so its settings variables are
  available.
- `PLATFORMS` and `ACTIONS` have been populated.
- All the store's own functions are defined, so you can call or wrap them.

Positional arguments follow the same pattern as the generated functions. Look at
the function you are replacing to see what it expects. `$2` is commonly the Steam
app ID.

## Returning results to the UI

Actions communicate back to Junk Store by printing JSON on stdout. If your
override needs to report success or a message, match the shape the original used.
A common one is:

```bash
echo "{\"Type\": \"Success\", \"Content\": {\"Message\": \"Done\"}}"
```

See [Action results](../reference/actions-and-types.md#action-results) for the shapes Junk Store
understands. If your action does not need to report anything, printing nothing is
fine.

## Testing your override

Overrides are picked up when the script is next run, so there is no regenerate
step. To check your file is valid shell before triggering it from the UI:

```bash
bash -n ~/.config/junkstore/overrides/Epic/store.sh
```

Then trigger the action from Junk Store and watch the logs. See
[Troubleshooting](../troubleshooting.md#reading-the-logs).

## Removing an override

Delete the file, or move it aside:

```bash
mv ~/.config/junkstore/overrides/Epic/store.sh{,.disabled}
```

The store returns to its normal behaviour immediately.

## Limits

An override can replace action functions. It cannot add a brand new action that
Junk Store does not already know about, because the UI builds its buttons from the
extension's registered action list. If you need new actions, that is
[authoring by hand](authoring-by-hand.md).
