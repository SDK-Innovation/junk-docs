# How Junk Store Pro finds your extension

Discovery is by directory and by naming convention. There is no registry file and no
install step, which is why an extension can be added simply by putting it in place.

An extension is found when it satisfies four things:

1. **It lives in the right place**, a directory under
   `~/.local/share/junkstore/scripts/Extensions/`. The directory name is the store
   name.
2. **It contains a `store.sh`.** The dispatcher sources `store.sh` from each
   extension directory. No `store.sh` means the extension does not exist as far as
   Junk Store Pro is concerned.
3. **Its `store.sh` registers the store name.** Generated scripts do this near the
   top with `PLATFORMS+=("MyStore")`, which is how the store announces itself.
4. **It contains a `static.json`.** This is what puts the extension on screen: its tab,
   where it is grouped, and the entries the interface offers for it.

Once registered, an action is dispatched by building a function name from the store
and the action, `<Store>_<action>`, and calling it if such a function exists.

### Two mechanisms, not one

The last requirement is worth separating from the others, because it works differently and
fails differently.

`store.sh` makes an extension **callable**. `static.json` makes it **visible**. Nothing joins
them up: a separate pass walks the whole `Extensions` tree, reads every `static.json` it
finds, and merges them into one document that describes the interface. Your extension's entry
is one fragment of that merged result.

So the two failure modes look nothing alike:

| Missing | Symptom |
|---|---|
| `store.sh` | Nothing runs. The extension is not there at all |
| `static.json` | Actions work if something calls them, but no tab appears |

Both files are written for you by generation, so this mostly matters when you are looking at
an extension that half works, or assembling one by hand.

Two practical consequences:

- **Copying a directory in is enough to be discovered**, provided its `store.sh`
  registers the correct name. If you copy an extension and forget to change the name
  inside `store.sh`, two directories will claim the same store name.
- **A directory with no `store.sh` is silently ignored.** There is no error, it just
  does not appear. If your extension is not showing up, check that file exists
  first.
- **A stray directory is still scanned.** Discovery has no notion of what is or is not
  meant to be an extension, so a backup copy of one, or a directory left behind by an
  experiment, is treated like any other. This is visible in practice: an `Amazon.bak`
  directory shows up in diagnostics as though it were a real extension.

All of this describes what is on disk. The files themselves come from the Generator, which
holds the definition and writes `store.sh`, `static.json` and the rest when you regenerate.
Discovery finds the scripts; the definition is where they come from. See
[The Generator](the-generator.md).

