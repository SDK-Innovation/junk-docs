# How launching works

Launching is a separate path from the actions an extension declares, which matters
because it means an override cannot change it.

**`launcher.sh` is what the Steam shortcut runs.** When a game is installed, Junk Store Pro
creates a Steam shortcut whose target is the extension's `launcher.sh`. So pressing play
on the game in your library, whether from Junk Store Pro or from the Steam library directly,
runs that script. Junk Store Pro does not have to be open.

```
Steam shortcut  (or the play button)
   -> launcher.sh
        exports runtime environment variables
        sources settings.sh
        evaluates TabShellEnvironment    (your tab config as shell variables)
        evaluates GameShellEnvironment   (that game's config as shell variables)
        resolves the game directory
        switches on the platform
   -> launchers/<Platform>
        does the actual work and runs the game
```

### launcher.sh is shared plumbing, the scriptlets are the custom part

This split is the important thing to understand:

- **`launcher.sh` is effectively static.** Extensions hardly ever touch it. It does the
  same setup for everyone: environment, settings, config as variables, game directory,
  then dispatch on platform. Treat it as plumbing rather than as a place to customise.
- **The scriptlets in `launchers/` are where the per platform work lives.** They are the
  custom part, and the place to make a change.

So if you need launch behaviour that settings cannot express, edit the scriptlet for
that platform. Reaching for `launcher.sh` is almost always the wrong move, and a change
there affects every platform rather than the one you meant.

The platform is chosen by the `platform` setting on the store or the individual game, and
`launchers/` holds one scriptlet per platform. Shipped scriptlets include `Proton`,
`Linux`, `Dosbox`, `RetroArch`, `ScummVM`, `Dolphin`, `Ryujinx`, and `Yuzu`.

Two more consequences worth knowing:

- **Your config values reach the launcher as shell variables.** That is what the
  two environment actions are for, and it is why most launch tuning is a settings
  change rather than a code change.
- **`launcher.sh` does not source your overrides file.** To change launch behaviour
  you either change settings or edit the platform scriptlet through the Generator's
  launchers editor.

Launch output is logged next to the game, in `launcher.log` inside the game
directory, which is the first place to look when a game does not start. Because the
Steam shortcut runs the script directly, that log is written whether or not Junk Store Pro
was open at the time.

