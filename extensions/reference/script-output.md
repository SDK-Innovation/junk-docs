# Script output: how scripts talk back

Custom scripts communicate with Junk Store by printing to standard output. There are two
formats, and which one you use depends on the script.

What follows covers the conventions shared by all of them. For which format a particular script
must produce, see [Custom scripts](custom-scripts.md). For the downloader, which has a richer
protocol of its own, see [Downloader protocol](downloader-protocol.md).

## Key and value lines

Most scripts, including the downloader, print `Label:Value` lines:

```
Status:downloading
Percent:42
```

**The labels are a fixed set, not free form.** This is the part that is easy to get wrong.
The parser recognises exactly nine labels, and it does two things with a line:

1. **Splits it.** The label must be letters only, and everything after the first colon is
   the value.
2. **Matches the label against the known nine.** A label outside that set is **discarded
   without a word**. There is no warning, no log entry at normal verbosity, and no error.

So inventing a label does nothing at all. Printing `Progress:42` instead of `Percent:42`,
or `State:done` instead of `Status:completed`, is not a variation on the protocol; it is
silently thrown away, and your download will appear to sit at zero or never finish.

The nine are `Status`, `Percent`, `Size`, `TotalSize`, `Speed`, `SpeedUnit`, `ETA`,
`Error`, and `Debug`. Each is described with its meaning and expected value under
[Keys you can emit](downloader-protocol.md#keys-you-can-emit).

Case matters too, since the labels are compared exactly. `percent:42` is not `Percent:42`.

Anything that does not parse as a label and value at all, such as ordinary log output from
a tool you called, is likewise ignored. That part is deliberate and useful: a downloader
can call `curl` or `unzip` and let their chatter fall on the floor. Just do not mistake
that tolerance for the labels themselves being open ended.

The same goes for the `Status` values, which are a known set rather than free text. See
[Status values](downloader-protocol.md#status-values).

## JSON

Several custom scripts print JSON instead. Which shape depends on the script, and there are
two distinct kinds. Getting these the wrong way round is a common mistake.

**Bare JSON, from custom scripts.** The scripts documented in [Custom scripts](custom-scripts.md) print the object or
array **directly**, with no wrapper. The caller parses it and reads the keys it wants:

| Script | Shape | Documented at |
|---|---|---|
| `getgameinfo` | One object describing a game | [Listing and metadata](custom-scripts.md#listing-and-metadata) |
| `loginstatus` | One object, `Username` and `LoggedIn` | [Login and accounts](custom-scripts.md#login-and-accounts) |
| `listusers` | An **array** of account objects | [Login and accounts](custom-scripts.md#login-and-accounts) |
| `get-launch-options` | One object, `exe`, `workingdir`, `gamedir` | [Launching](custom-scripts.md#launching) |
| `diagnostics` | One object, `summary` and a `results` array | [Diagnostics](custom-scripts.md#diagnostics) |

Do **not** wrap these in a `Type` and `Content` envelope. A wrapped `getgameinfo` parses as
valid JSON but none of the expected keys are found, so every field silently comes back empty
and you get a game with a blank title rather than an error.

**Envelopes, from actions.** Actions in the command map are the ones that print
`{"Type": ..., "Content": ...}`, described in
[Action results](actions-and-types.md#action-results):

```json
{"Type": "Success", "Content": {"Message": "Done"}}
```

That is a different layer from the custom script hooks. If you are writing one of the scripts
listed above, print bare JSON.

**Errors.** Where an error shape is accepted it is `{"error": "..."}`, lower case, and not the
envelope's `Error` type. `getgameinfo` accepts it.

**Failures are usually silent.** These callers run your script ignoring its exit status, and
several catch parse errors and substitute an empty result rather than reporting them. So
malformed JSON tends to show up as missing data, not as an error message. When a script's data
is not appearing, run it by hand and pipe it through a JSON parser before looking anywhere
else:

```bash
~/.local/share/junkstore/scripts/Extensions/MyStore/getgameinfo somegame | python3 -m json.tool
```

Use key and value lines for progress and state; use JSON for results and structured
content.
