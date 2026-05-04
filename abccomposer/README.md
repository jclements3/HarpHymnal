# abccomposer

Custom ABC composer — single self-contained web page with a horizontal
40 / 40 / 20 layout:

```
+-------------------+-------------------+----------+
|  ABC editor       |  abcjs render     |  Claude  |
|  (CodeMirror 5    |  (live, debounced |  chat    |
|   + vim keymap)   |   on every edit)  |  pane    |
+-------------------+-------------------+----------+
```

No build step, no server (except for the Claude pane, which talks to
api.anthropic.com directly). All deps are vendored under `vendor/`.

## Run it

```bash
xdg-open /home/james.clements/projects/HarpHymnal/abccomposer/index.html
# or any other browser launcher
```

For the audio (`▶ Play` button) you need a browser context that allows
the WebAudio API. `file://` works in Firefox; Chrome may want you to
serve the directory:

```bash
cd abccomposer && python3 -m http.server 8765
# then http://localhost:8765/
```

## First-time setup

1. Click `⚙` in the toolbar.
2. Paste an Anthropic API key (starts `sk-ant-...`). Stored in browser
   `localStorage` only — never leaves your machine except as the
   `x-api-key` header on the direct call to `api.anthropic.com`.
3. Pick a model (default: `claude-opus-4-7`).
4. Optionally edit the system prompt. The current ABC source is
   appended automatically as `<current_abc>...</current_abc>` on every
   request, so don't include it in the system prompt itself.

## Editor

CodeMirror 5 with the official `vim` keymap. Drops you straight into
NORMAL mode. The full vim subset that the keymap ships with is
available — motions, operators, text objects (`iw`, `i"`, etc.),
visual-block, marks, registers, macros (`q`), dot-repeat, `/` `?`
search, `:s/pat/rep/g` / `:%s/...`, `u` / `Ctrl-R`. Substantially more
complete than the hand-rolled `easyabc_vim/` patch.

Custom ex commands:

| ex command  | effect                       |
| :---------- | :--------------------------- |
| `:w`        | download current buffer as `.abc` (uses the filename input) |
| `:play`     | play via abcjs synth         |
| `:stop`     | stop playback                |

ABC syntax mode is defined inline in `index.html` —
header lines (`X:`, `T:`, `K:`, ...), `%` comments, `!decoration!`,
`"chord symbol"`, bar lines, accidentals, and notes are all colored
per the dracula theme.

## Render pane

`ABCJS.renderAbc` runs 250 ms after the last keystroke. Errors render
inline as red text in the score area.

## Chat pane

Each turn includes:

- `system` = your saved system prompt **plus** the current ABC source
  wrapped in `<current_abc>...</current_abc>`
- `messages` = the visible (`user` + `assistant`) chat history

Messages persist in `localStorage` (`abccomposer.chatHistory`). Click
`Clear` to reset.

When an assistant message contains a fenced ` ```abc ` block (or just
` ``` `), an **→ Apply to editor** button appears beneath the code
block. Click it and the editor is replaced with that block's contents.

## Why CodeMirror 5 (not CM6)

CM5 ships as standalone JS+CSS files droppable into `vendor/`. CM6
requires a bundler (rollup/esbuild + ES module imports + a vim
extension), which would mean adding a build step to a repo that
currently has none. The CM5 `vim` keymap has been the de-facto vim
implementation for browsers for over a decade and supports the full
feature set we want.

## Why a separate top-level app (not a `tablet_app/` tile)

- Composing happens at a desktop with a real keyboard, not on the P90
  WebView.
- The Anthropic API call needs a key, which we don't want bundled into
  the Android APK.
- The render pane is a pure abcjs DOM target; the tablet app's HTML
  tiles are pre-baked and don't need a code editor.

If a tablet-side viewer is wanted later, it's a 30-line `viewer.html`
that just calls `ABCJS.renderAbc` on a bundled `.abc` file — separate
concern.

## Vendored deps (under `vendor/`)

| file                     | what                              |
| :----------------------- | :-------------------------------- |
| `codemirror.css/.js`     | CodeMirror 5.65.18 core           |
| `dracula.css`            | dark theme                        |
| `vim.js`                 | vim keymap                        |
| `dialog.css/.js`         | needed by vim ex prompt           |
| `search.js`              | `/` `?` search                    |
| `searchcursor.js`        | search engine                     |
| `matchbrackets.js`       | `%` motion                        |
| `abcjs-basic-min.js`     | abcjs 6.4.4 (render + synth)      |

All are MIT / 3-clause BSD. No build step. No package.json changes.
