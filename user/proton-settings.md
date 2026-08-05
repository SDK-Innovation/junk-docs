# Proton settings

For games that run under Proton, the second editor on
[the game's cog](game-settings.md) is where the interesting settings are. It's the largest
of them, and unlike the DOSBox one it's worth going through: anti-cheat runtimes, frame
limiting, upscaling, and frame generation.

## Proton settings

For games that run under Proton, the second editor is where the interesting settings are.
It's the largest of them, and unlike the DOSBox one it's worth going through, because most
of it is things people genuinely want: anti-cheat runtimes, frame limiting, upscaling, and
frame generation.

### How these actually reach the game

Worth understanding once, because it explains the whole screen.

**Every setting you fill in becomes an environment variable when the game launches.** Junk
Store turns the saved configuration into a list of variables, and the launch script applies
them just before starting the game. Nothing is written into the game's files, and nothing is
changed permanently.

**The variable's name usually comes from the section it's in.** A setting called
`MULTIPLIER` in the **LSFG** section becomes `LSFG_MULTIPLIER`, which is exactly the name
the frame generation layer looks for. That's the point of the grouping: the section name
makes the variable come out with the name the tool expects.

Some settings opt out of that and are passed through under their own names, everything in
the **Environment** section, which is why `LANG` there is simply `LANG`, and a few
individual ones like **Disable LSFG-VK**.

**Empty means absent, not empty.** A field you haven't filled in produces no variable at
all, so the game sees exactly what it would have seen if the setting didn't exist. That's
why clearing a field is a genuine undo here, and it's the first thing to try when something
misbehaves.

Two consequences worth knowing:

- **Nothing takes effect until the next launch.** Changing a setting while a game is running
  does nothing to it.
- **The launcher writes `launcher.log` into the game's own folder** as it starts, recording
  what it applied and what it ran. If a setting doesn't seem to be doing anything, that's
  where to look. Opening [the File Manager](file-manager.md) from the game's menu puts you in
  that folder already, and the
  [text viewer](file-manager-tools.md#viewing-files) reads it on the device.

### Runtimes

The main section, visible without raising the level.

| Setting | Does |
|---|---|
| **Easy Anti-Cheat** | Turns on Steam's anti-cheat runtime for this game. Some online games won't start without it |
| **BattlEye** | The same, for games using BattlEye |
| **ESYNC** / **FSYNC** | Two ways of speeding up how the game handles threads. Often a performance win, occasionally the cause of a crash |
| **Pulse Audio Latency ms** | Reduces audio delay. Worth trying for a game whose sound lags behind the picture |
| **VKD3D** / **VKD3D-Proton** | Alternative ways of running DirectX 12 games |
| **DXVC HDR** | HDR output, offered as **Enable** or **Disable**. It sits at **Disable**, which is what you want on a Deck without an HDR screen |
| **RADV_PERFTEST** | Experimental driver features: `gpl`, `aco` or `amdvlk`. Leave empty unless told otherwise |
| **FSR Strength** | AMD's upscaling. `0` is off, and higher numbers trade sharpness for frame rate |
| **Limit Framerate** and **Frame Rate** | Caps the frame rate. Both are needed: the first turns it on, the second sets the number |
| **Force Large Address Aware** | Lets an older 32-bit game use more memory. The fix for some games that crash after a while |

**Anti-cheat runtimes may need installing first.** They come from Steam, and if the game
still won't start, that's usually why. The setting turns on a runtime; it can't fetch one.

**Limit Framerate is a pair.** Turning it on without setting a number, or setting a number
without turning it on, does nothing. A frame cap is often the single best thing for battery
life, so it's worth getting right.

### Advanced

Raise the level to **Expert** to see these. Most people never need them, and one of them
does nothing at all, it's noted in the table.

| Setting | Does |
|---|---|
| **Additional Variables** | Extra environment variables, for a game that needs something unusual. **Each one has to start with `export`**: see below |
| **Additional Arguments** | Extra options passed to the game itself, such as `-windowed` or `-nolauncher` |
| **Custom Mesa ICD** | Uses a graphics driver file you've put in place yourself, at `~/mesa/share/vulkan/icd.d/` |
| **Ignore EGS Arguments in launcher** | Drops the arguments the Epic launcher would normally add. For games those arguments break |
| **Set Steam Compatibility Library Paths** | On by default. Leave it on unless a game can't find its own files |
| **Set Proton Game Drive** | On by default. Presents the game's folder as its own drive letter. Turn it off for a game that insists on running from C: |
| **Hack to show windows hidden by gamescope** and its **Delay** | Nothing. Left over from an experiment that was never finished, so setting them has no effect |

#### Additional Variables needs `export`

**Write `export NAME=value`, not `NAME=value`.** This is the one thing to get right here,
and it's easy to miss.

```
export WINEDEBUG=-all
```

What you type is run as a line of script just before the game starts. Without `export`, the
value is set and then goes no further: the game is a separate program, and it only inherits
variables that were exported. So `WINEDEBUG=-all` on its own is accepted, saves without
complaint, and does nothing at all.

**Nothing warns you**, because a setting without `export` is perfectly valid script, it
just isn't useful. If you've copied a variable from a forum post and it seems to have no
effect, this is almost always why. Advice written for a command line often omits `export`,
because there it isn't needed.

**This is ordinary Linux behaviour rather than a Junk Store rule**, which is why it's worth
knowing rather than merely remembering. The same distinction applies in any shell script you
ever write.

**For more than one, press Y on the field.** That opens a **Text Editor** window with room
for several lines, which is much easier than trying to fit them into the field itself. Put
each on its own line, each with its own `export`:

```
export WINEDEBUG=-all
export DXVK_HUD=fps
```

The editor is the sensible way to work with this setting even for one variable, since you
can see the whole thing at once.

**It's a real escape hatch**, and worth the care. Anything you put there runs as script, so
it's the answer for the one-off fix a forum post tells you about, and the place to be
careful about what you paste in.

### LSFG: frame generation

**LSFG** is Lossless Scaling Frame Generation: it inserts generated frames between real
ones, so a game running at 30fps can present at 60. On a Deck that can be the difference
between a game feeling playable and not.

**It needs Lossless Scaling and lsfg-vk installed before any of this does anything.**
Junk Store doesn't install either. These settings only pass your choices along to the layer;
if it isn't there, they do nothing at all, silently. **Setting it up is covered on the Junk
Store website**. Start there, then come back to this screen.

#### Why this section looks the way it does

The names here are rougher than elsewhere: two switches to turn one thing on, a setting
called *Disable* that you set to *Enable*, options named after the variables they set rather
than what they do.

**That's because none of this was programmed.** Support for frame generation was added
entirely by editing a configuration file, no new code in Junk Store, no update to the
launcher, nothing rebuilt. The settings you see are that file's contents, and the names came
across from the tool they're passed to.

It's a fair illustration of how the settings system works: a section's name becomes the
prefix on what it hands to the program, so putting the right names in the right section is
all that's needed to support something new. The cost is that the labels are the tool's, not
ours, and they read like it.

The names not being ours is also the reason they're worth learning. They're
[the tool's own](introduction.md#it-doesnt-hide-how-things-work), so anything you read
elsewhere about configuring frame generation applies here directly, rather than needing
translating out of a friendlier vocabulary Junk Store invented.

Worth knowing mainly so the oddness reads as what it is. The settings do work; they just
weren't dressed up.

Once it's installed, the settings are per game:

| Setting | Does |
|---|---|
| **Disable LSFG-VK** | The on/off switch, despite the name. Set to **Disable** to begin with, so this is the first thing to change |
| **Enable Legacy LSFG** | Required for any of the rest to work. Set it to **Enable** as well: see below |
| **FPS Multiplier** | How many frames to present for each real one. `2` doubles it |
| **Flow Scale** | Quality of the motion analysis, `0.8` by default. Lower is faster and rougher |
| **Performance Mode** | Trades quality for speed |
| **Disable FP16** | Turns off half-precision maths. It's faster on AMD, so only disable it if you see artefacts |
| **GPU** | Which GPU to use, by name or ID. Empty means the main one, which is right on a Deck |
| **Lossless.dll Path** | Where `Lossless.dll` is, if you installed Lossless Scaling somewhere unusual. Empty uses the normal Steam location |
| **Frame Pacing** | How generated frames are timed: **None**, **VSync** or **Adaptive** |
| **HDR Mode** | Better colour on an HDR screen, at some cost in speed |
| **Experimental Present Mode** | **FIFO**, **VSync**, **Mailbox** or **Immediate**. Affects smoothness and input lag |

#### Turning it on takes two settings

**Set both of these to Enable**, and the rest can be left alone:

1. **Disable LSFG-VK → Enable**
2. **Enable Legacy LSFG → Enable**

**Both are needed.** The first switches frame generation on for this game. The second is
what makes the rest of the settings on this screen reach it, without it, your multiplier,
flow scale and the others are ignored, and you'll get default behaviour or nothing at all.

**That second one is the usual reason people conclude LSFG doesn't work.** Nothing indicates
it's required, and it reads like an option for an older version. It isn't optional.

**The first one's name doesn't help either.** It reads as though setting it would switch
frame generation off, but it's a two-way choice, **Enable** or **Disable**, sitting at
Disable to begin with.

With both on, the default multiplier of `2` is the setup most games want. Everything else is
there for when a particular game doesn't cooperate.

**Frame generation is not free.** It costs some latency, and generated frames can show
artefacts on fast movement, most visible around thin objects and screen edges. Some games
suit it; some don't. It's per game precisely because that judgement is per game.

**If it isn't working**, check in this order:

1. **Lossless Scaling and lsfg-vk are actually installed.**
2. **Both switches are on**: Disable LSFG-VK *and* Enable Legacy LSFG. Missing the second
   is the most common cause, and it looks like the settings simply doing nothing.
3. **The launcher log** in the game's folder, which records what was applied.

### The emulator's own configuration

The other entry is named after what it configures, such as **dosbox 1-0** or
**dosboxx 1-0**, and it edits that emulator's actual configuration file.

**This is a large amount of settings, and they're not Junk Store's.** A DOSBox
configuration covers CPU cycles, memory sizes, sound cards, joystick emulation, video
scaling and a great deal besides, hundreds of settings, each meaning what the DOSBox
project says it means. Junk Store presents them and saves them; it doesn't define them.

So rather than describe them here, use the documentation for the emulator itself:

- **DOSBox**: [dosbox.com](https://www.dosbox.com/wiki/) documents the standard
  configuration file
- **DOSBox Staging**: [dosbox-staging.github.io](https://dosbox-staging.github.io/)
- **DOSBox-X**: [dosbox-x.com](https://dosbox-x.com/wiki/)

Anything those say about a setting applies here, since it's the same file.

**What Junk Store adds is being able to edit it in Game Mode**, per game, without a text
editor or Desktop Mode. The visibility dropdown at the top is worth using: on **Basic** you
see the handful of settings people actually change, and the full list is there when you want
it.

**A game that ran and now doesn't, right after you changed something here**, is almost
always the change. Start on the field puts one setting back; Start on the dropdown resets the
whole file to what the game shipped with.

## Bat Files

DOS games often come with `.bat` files that set things up before the game runs. Where a game
has them, **Bat Files** lets you read and edit them on the device.

This is for the case where a game's batch file needs a small change: a path that's wrong, an
option that needs adding. If you don't already know what's in these files, you don't need
this editor.
