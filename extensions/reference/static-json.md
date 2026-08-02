# static.json

`static.json` is what puts an extension on screen. `store.sh` makes it callable; this file
makes it visible, and the two are independent. An extension with no `static.json` still has
working scripts and no tab.

**Generation writes it because it is hard to get right by hand.** That is the reason, rather
than convenience. Nothing checks a `static.json` against the extension it belongs to: the
identifiers it uses have to match what `store.sh` actually exposes, and if they do not, the
file is still valid JSON, still merges cleanly, and produces an interface that does nothing.
There is no error to read.

So this section is written to be understood rather than acted on. Knowing the shape helps
when something has half appeared, and the merge behaviour below is worth knowing because it
leaves room to add to the interface rather than only describing your own extension. Getting a
change to stick still means putting it in the Generator definition.

## How it is read

A pass walks the whole `Extensions` tree, opens every `static.json` it finds, and merges them
into one document. That merged document is what the interface is built from. Your extension's
file is a fragment of it, not a self contained description.

A malformed file is skipped rather than aborting the pass, so one broken fragment does not
stop the others being read. It is not free, though: see
[Editing it by hand](#editing-it-by-hand).

## The shape

A top level object whose keys name pieces of interface. A shipped extension has around
fifteen. Each value has a `Type` and a `Content`.

```json
{
  "games-tabs": {
    "Type": "StoreTabs",
    "Content": {
      "Tabs": [
        { "ActionId": "GetEpicActions", "Type": "GameGrid", "Title": "Epic" }
      ]
    }
  }
}
```

That fragment is the whole reason an Epic tab exists.

| Type | What it describes |
|---|---|
| `StoreTabs` | Tabs along the top, each naming the action that fills it |
| `MainMenu` | Panels and sections on the main menu |
| `ActionSet` | A named group of actions the interface can invoke |
| `ScriptSet` | A group of script driven actions |

Actions inside a set are the individual entries:

```json
{
  "Id": "GetTabShellEnvironment",
  "Type": "Shell",
  "Command": "./scripts/junk-store.sh Epic gettabshellenvironment",
  "Title": "Gets the tab settings as shell variables"
}
```

`Command` is what runs. `Type` tells the interface what to expect back, using the same values
described in [Actions, results, and types](actions-and-types.md#action-types).

## Merging is additive, and that is the interesting part

When two fragments use the same key, they are not one-overwrites-the-other. Entries are
matched on their fields other than `Actions`, and where an entry matches, **the incoming
actions are appended to the existing ones**, skipping any already present.

The consequence is worth stating plainly: **a fragment can add actions to a set another
extension defined.** If your `static.json` names an existing set and lists an action, that
action joins the set rather than replacing it. That is how an extension can contribute a
button to a menu it does not own.

The caution from the top of this section applies most sharply here. Contributing an action
means naming a set and an action id that already exist, exactly, with no check that either is
right. Get the set name wrong and your entry lands somewhere harmless and invisible; get the
action id wrong and you have added a button that does nothing. Copy the identifiers from a
generated file rather than typing them.

Three things follow.

**Adding is easy, removing is not.** The merge only ever adds. There is no way to express
"take that entry away", so a fragment cannot suppress something another extension contributed.

**Order is not yours to control.** Which fragment is read first depends on directory walk
order, so do not write anything that depends on your action landing in a particular position.

**Duplicates collapse quietly.** An identical action contributed twice appears once. That
makes accidental duplication harmless and deliberate duplication impossible.

## Editing it by hand

**Prefer not to.** A regenerate overwrites the file, so a hand edit is temporary unless you
have stopped regenerating that extension entirely, and the failure modes are quiet ones.

Two kinds of mistake, neither of which announces itself:

- **A malformed file** is skipped, and the parse error is printed on standard output, which is
  the same stream the collected result is returned on. So a JSON syntax error costs you that
  extension's interface and puts a stray line into the response, which can affect more than
  the extension you broke.
- **A well formed file with a wrong identifier** merges perfectly and gives you an interface
  element wired to nothing. Nothing validates that an `ActionId` corresponds to an action the
  extension actually has.

The second is the one that costs an afternoon, and it is why the file is generated rather
than written.

If you are going to edit it anyway, for an extension you maintain by hand and do not
regenerate, at least confirm it still parses before restarting:

```bash
python3 -m json.tool ~/.local/share/junkstore/scripts/Extensions/MyStore/static.json >/dev/null
```

That catches the first kind of mistake and none of the second. For anything you intend to
keep, put it in the Generator definition and let generation write the file.

## Related

- What makes an extension discoverable at all:
  [How Junk Store finds your extension](../concepts/how-extensions-are-found.md)
- The `Type` values an action can carry:
  [Actions, results, and types](actions-and-types.md)
- Where the definition that generates this lives:
  [The Generator](../concepts/the-generator.md)
