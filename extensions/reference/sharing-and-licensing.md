# Sharing, export, import, and licensing

An extension can be written out as a single JSON file and read back in. That file is the
whole extension, so it is what you share, what you back up, and what you commit to git.

What follows covers the commands, and the workflow of keeping an extension version
controlled. It is how the shipped extensions are maintained.

## The commands are on the command line

The Generator lists **Import the preset from a file** and **Export the preset to a file**
in its menu, but the working route for both is the command line.

For export that is a detail. For import it is a deliberate speed bump: importing an
extension runs its code, so requiring a terminal means whoever imports has the file on disk
and typed the extension's name, rather than tapping something a stranger linked. See
[Only import extensions from people you trust](#only-import-extensions-from-people-you-trust).

**Use the `junk-store` binary.** The command line versions take the directory and the
extension name as arguments.

Switch to Desktop Mode, or connect over SSH, and run:

```bash
JS="$HOME/.local/share/junkstore/junk-store Generator"

# Export: database -> <dir>/<Name>.json
$JS exportpresetfile /path/to/dir MyStore

# Import: <dir>/<Name>.json -> database
$JS importpresetfile /path/to/dir MyStore
```

The file is always named after the extension, so exporting `MyStore` into a directory
produces `MyStore.json` there, and importing looks for that same name.

### The other verbs you will want

```bash
# Import the extension's scripts from its directory into the database
$JS importscripts MyStore
```

`importscripts` is the command line equivalent of **Save scripts back to DB**. It matters
for the same reason described in
[Authoring by hand](../guides/authoring-by-hand.md#order-matters-and-getting-it-wrong-loses-your-work):
run it before exporting, or you export the database's old copy of your scripts rather
than the ones you edited.

## The round trip

Three places hold your extension:

| Place | Holds |
|---|---|
| The extension directory | The scripts you edit |
| The database | What generation reads |
| `<Name>.json` | What you commit or send |

Four commands move between them, and each one goes one way only:

| Command | From | To |
|---|---|---|
| `importscripts` | Extension directory | Database |
| `exportpresetfile` | Database | `<Name>.json` |
| `importpresetfile` | `<Name>.json` | Database |
| Regenerate | Database | Extension directory |

Everything passes through the database, which is why there is no single command that takes
your edited scripts straight to a shareable file.

Read it as two directions:

- **Saving your work:** `importscripts`, then `exportpresetfile`, then commit the JSON.
- **Restoring or receiving:** `importpresetfile`, then regenerate to write the scripts
  out.

## Keeping it in git

The exported JSON is a single text file describing the whole extension, which makes it
well suited to version control. Committing it gives you history for the extension as a
unit, not just the loose scripts.

**Keep a repository holding a shipped extension private.** Versioning your own local copy
of Epic, Amazon, GOG, or Itch is a reasonable thing to do, and nothing stops you. Pushing
that repository to a public host is redistribution, and is not permitted. The safe habit is
one repository per extension, so a public one never has a shipped extension's export in its
history. Bear in mind that git keeps history: removing the file in a later commit does not
remove it from a repository you have already published.

Set up a repository for the extension:

```bash
mkdir -p ~/my-extensions/MyStore
cd ~/my-extensions/MyStore
git init
```

Then each time you reach a good state:

```bash
JS="$HOME/.local/share/junkstore/junk-store Generator"

$JS importscripts MyStore              # your edited scripts -> database
$JS exportpresetfile "$PWD" MyStore    # database -> MyStore.json here
git add -A && git commit -m "what changed"
```

To go back to a previous state:

```bash
git checkout <commit> -- MyStore.json
$HOME/.local/share/junkstore/junk-store Generator importpresetfile "$PWD" MyStore
# then run Regenerate installed extensions
```

That is the recovery path. Because the export captures the definition rather than just
the files, restoring a commit restores the actions, the settings, and the scripts
together.

### Why bother

- **Real history.** You can see what changed between two versions of the extension, and
  which change broke something.
- **Recovery from the overwrite trap.** Regenerating writes files from the database. If
  that loses an edit, a committed export is a known good state to import back.
- **Moving between machines.** Clone the repo on another Deck, import, regenerate.
- **Sharing.** The same file you commit is the file you hand to someone else.

### What is and is not captured

The export is the extension definition: actions, settings, scripts, launchers,
placement. It does **not** include your games, their per game configuration, or
downloaded artwork. Those live in the store's own database and are yours, not part of the
extension.

Also note that a few settings are deliberately left out of an export: the SSH user, SSH
host, ROMs path, and the use SSH flag. Those describe your machine rather than the
extension, so expect to set them again after importing on a different setup. That
includes importing your own export onto a second machine.

## Sharing with someone else

**Read the licensing section below before you share anything derived from a shipped
extension.**

To give an extension you created to another person:

1. `importscripts` then `exportpresetfile` as above.
2. Send them the `<Name>.json`.

For them to use it:

1. Put the file somewhere on their Deck.
2. `importpresetfile <dir> <Name>`.
3. Run **Regenerate installed extensions**.

Sending someone the file is the way to share an extension. Distributing through Junk
Store itself is not something you can do; the extensions offered in **Download preset
from server** are published by the Junk Store project.

## Only import extensions from people you trust

**An extension is executable code, not a settings file.** Importing one and regenerating puts
shell and Python scripts on your machine that Junk Store will run. Treat receiving a `.json`
export exactly as you would treat being sent a shell script and told to run it.

What an imported extension can do, if its author intended harm:

- **Run as you, with your permissions.** Scripts are executed directly, with no sandbox and no
  confinement. Anything you can do from a terminal, an extension script can do: read or delete
  your files, read your saves and configuration, reach the network, install other software,
  add things that persist across reboots.
- **Run before you choose to do anything with it.** This is the part people get wrong. Code
  does not wait until you press install. To find out which stores exist, Junk Store sources
  every extension's `store.sh`, and each `store.sh` sources its own `settings.sh` at the top.
  So an imported extension gets to run code simply by being present. Importing it *is* running
  it.
- **Look completely ordinary while doing it.** A malicious extension can list games, install
  them, and work exactly as advertised. Nothing about it behaving correctly tells you it is
  safe.

The `.json` export is the risky artefact specifically because it is one file that looks like
data. It contains every script as embedded text, so the whole payload arrives in something
that reads like configuration.

**Before importing an extension somebody sent you:**

- **Know who wrote it.** This is the only protection that really works. Everything else is a
  spot check.
- **Read the scripts.** The export is text. Open it in the file manager's text viewer, or in
  any editor, and read what the scripts do. They are short, and the shipped ones are a good
  baseline for what normal looks like.
- **Be suspicious of anything reaching outside the game directories.** A downloader fetching a
  game is expected. A script touching `~/.ssh`, your browser profile, your Steam
  configuration, or piping a download straight into a shell is not.
- **Be equally careful with generated extensions.** An extension written for you by an AI
  assistant deserves the same reading as one from a stranger. It is not malicious, but it is
  not reviewed either, and it will run with the same permissions.

None of this is unique to Junk Store; it is the ordinary risk of running someone else's code.
It is worth stating plainly because an extension arrives looking like a settings file rather
than like a program.

**This is why importing is a command line operation.** There is no button in the interface
that installs an extension from a file, and that is a deliberate choice rather than a missing
feature. The friction is the safeguard: importing from a terminal means you have the file, you
know where it came from, and you typed the name. A menu item would make it a single tap on
something a stranger linked, which is exactly the wrong amount of effort for an operation that
runs arbitrary code.

The same reasoning applies to mistakes, not just malice. Most damage will come from a
well-meaning extension with a wrong path in an uninstall script, or one generated by an AI
assistant that half works. That risk rises with how easy importing is, and no amount of
trusting the author protects against it.

If you maintain an extension others use, publishing it somewhere with a visible history, such
as a git repository, lets people see what changed between versions rather than trusting each
export on faith.

## What you may and may not share

**Open and redistributable are two different things**, and the distinction runs through
everything below.

Every extension on your device is open to you in the sense that matters day to day. You can
read every line of the shipped ones, change them on your machine, learn from how they work,
and copy their techniques into an extension of your own. Nothing is compiled, obfuscated, or
hidden behind an API, which is why this guide can describe the whole surface. That is a
deliberate choice, not an oversight.

What you do not get with the shipped extensions is the right to pass their code on to other
people. Those are separate permissions, and having the first has never implied the second.

This matters, because an export is a complete copy of whatever it contains, including
code you did not write.

**Extensions you created are yours to share.** An extension the wizard generated for you,
and whatever you then wrote into it, is your work. Export it, publish it, put it on a
public repository, do as you like.

**The Epic, Amazon, GOG, and Itch extensions are not yours to redistribute.** Their code
is **source available, not open source**. You can read it, run it, and modify your own
copy, because it ships with the product and is on your machine. That is not the same as a
licence to redistribute it. Specifically, do not:

- Share or publish those extensions' `.json` exports.
- Copy their scripts into an extension you then distribute.
- Publish a modified version of any of them.

**The line is authorship, not effort.** If your extension contains scripts lifted from a
shipped one, sharing it redistributes that code regardless of how much you changed around
it. Templates the Generator produced for you are fine; code from Epic, Amazon, GOG, or
Itch is not.

If you want to share a fix for one of those extensions, describe the change or send the
diff to the Junk Store project rather than distributing a modified copy. That also means
the fix reaches everyone rather than only the people you sent it to.

This is a summary for practical guidance, not the licence itself. If you intend to
distribute something and are unsure whether you may, ask before you publish.

## A pattern worth copying

Treat the exported JSON in your repository as the source of truth, and the Generator
database as a working copy. Two habits follow:

- **Before you start editing**, import the committed JSON so the database matches what
  you last committed.
- **When you finish**, `importscripts` then `exportpresetfile` back into the repository,
  and commit.

That way the committed file is authoritative, rather than relying on whatever state the
database happens to be in. It also makes the git history meaningful, since each commit is
a complete extension rather than a partial snapshot.

## Related

- The edit and regenerate workflow: [Authoring by hand](../guides/authoring-by-hand.md)
- What the Generator operations do: [Generator settings](../concepts/the-generator.md)
- Getting an extension in the first place: [Quick start](../guides/quickstart.md)
