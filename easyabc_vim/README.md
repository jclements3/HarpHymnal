# easyabc_vim

Embedded vi keybindings + file-watcher mode for [jwdj/EasyABC](https://github.com/jwdj/EasyABC), driven from this repo so we can patch a fresh upstream clone reproducibly on any box.

## Quick install

```bash
./install.sh
```

That clones `jwdj/EasyABC` into `~/projects/HarpHymnal/tmp/EasyABC`, drops in the vi modules, patches `easy_abc.py`, and installs a `~/.local/bin/easyabc` shim. Re-runnable; the patch is idempotent.

Requires `python3-wxgtk4.0` on Ubuntu (`sudo apt install python3-wxgtk4.0 fluidsynth`).

## What you get

- **Vi mode** in EasyABC's editor pane — starts in NORMAL by default. F12 toggles off.
  Subset implemented: `hjkl`, `w/W b/B e/E`, `0 ^ $`, `gg G`, `%`, `f F t T`, counts, `d c y` + motions, `dd cc yy`, `D C Y`, `x X p P r{c} ~`, `i a I A o O`, visual mode (`v V`), `u` / `Ctrl-R`, `/` `?` `n` `N`, `:w :q :wq :s/pat/rep/[g]`, `:%s/...`.
- **Vim-as-editor workflow** (`:watch`) — EasyABC polls the loaded file's mtime every 500 ms; when vim saves the same file, EasyABC reloads + re-renders. Editor goes read-only while watching so vim stays the source of truth.
- **AUI compat shim** (`aui_compat.py`) — silences a wxPython 4.x crash in `auibar.DrawSeparator` (`rect.x += rect.width/2` integer/float mismatch).
- **Self-test harness** (`test_vi.py`) — mocks wx + Scintilla, drives synthetic key events through ViMode. Run after install:
  ```bash
  python3 ~/projects/HarpHymnal/tmp/EasyABC/test_vi.py
  ```

## Files

| File | Role |
|---|---|
| `vi_motions.py` | pure-position motions (`h/j/k/l`, words, `0/^/$`, `gg/G`, `%`, `f/F/t/T`) |
| `vi_operators.py` | `d/c/y`, `p/P`, `r{c}`, `~`, register state |
| `vi_search.py` | `/ ? n N`, `:s/pat/rep/[g]`, `:%s/...` |
| `vi_mode.py` | mode state machine, key dispatch, F12 toggle |
| `aui_compat.py` | wxPython 4.x AUI integer-cast monkeypatch |
| `test_vi.py` | self-test harness (mocks wx, asserts buffer/cursor state) |
| `install.sh` | clone + patch + shim install |
| `patch.py` | idempotent string-anchored patcher for upstream `easy_abc.py` |

## Vi commands

### Modes
- `i` `a` `I` `A` — insert at / after caret, line-start, line-end
- `o` `O` — open line below / above
- `v` `V` — visual / linewise visual
- `Esc` / `Ctrl-[` — back to NORMAL
- `F12` — disable vi mode entirely (escape hatch)

### Motions (counts work as prefix)
- `h j k l` `←↓↑→` `Enter` `Backspace`
- `w W b B e E` — words / WORDs
- `0 ^ $` — line start / first non-blank / line end
- `gg G` `n+G` — document start / end / line N
- `% f<c> F<c> t<c> T<c>` — match brace / find char

### Operators (operator + motion, or doubled for line)
- `d c y` — delete / change / yank
- `dd cc yy D C Y` — linewise / to-end-of-line shortcuts
- `x X` — delete char right / left
- `p P` — paste after / before
- `r{c}` — replace char
- `~` — toggle case
- `s S` — substitute char / line
- `u` `Ctrl-R` — undo / redo

### Ex commands
- `:w` `:q` `:wq` `:w!` `:q!` `:x` — save / close
- `:s/pat/rep/[g]` `:%s/pat/rep/[g]` — substitute (current line / whole buffer)
- `:e <path>` — load file
- `:e` `:reload` — reload current file
- `:play` `:stop` — playback
- `:watch` — start polling current file's mtime; reload on change; editor read-only
- `:nowatch` — stop watching

### Search
- `/text<Enter>` — search forward
- `?text<Enter>` — search backward
- `n N` — next / previous match

## Vim-as-editor workflow

```bash
# Terminal 1 — viewer/player
easyabc creed/foo.abc

# In EasyABC's editor (NORMAL mode):
:watch                    # title shows [watching]; editor read-only

# Terminal 2 — actual editing
vim creed/foo.abc
# edit, :w  →  EasyABC re-renders within 500 ms

# In EasyABC, type :play to hear it. :stop to halt.
```
