/*
 * Vim regression suite for the abccomposer's CodeMirror editor.
 *
 * Loaded in the running WebView via evaluateJavascript. Each test
 * resets the editor to a known buffer + cursor, dispatches a sequence
 * of vim keys through CodeMirror.Vim.handleKey (the same path used
 * for letter taps from the IME via handleVimKey), then compares the
 * resulting buffer & mode against expectations.
 *
 * Results are written to window.__VIM_TEST_RESULTS as a JSON string
 * so the harness on the host can adb-pull via document.title.
 */
(function () {
  if (!window.cm || !window.CodeMirror || !CodeMirror.Vim) {
    document.title = "VIMTEST: cm/Vim missing";
    return;
  }
  const Vim = CodeMirror.Vim;
  const cm  = window.cm;

  function reset(text, line, ch) {
    cm.setValue(text);
    cm.setCursor({ line: line || 0, ch: ch || 0 });
    // Ensure normal mode.
    Vim.handleKey(cm, "<Esc>", "user");
  }
  function send(keys) {
    // Each entry: a single vim key, e.g. "d", "<Esc>", "i", "<C-c>".
    for (const k of keys) Vim.handleKey(cm, k, "user");
  }
  function isInsert() { return !!(cm.state.vim && cm.state.vim.insertMode); }
  function isNormal() { return !!(cm.state.vim && !cm.state.vim.insertMode && !cm.state.vim.visualMode); }

  const cases = [
    {
      name: "i enters INSERT mode",
      setup: ["abc", 0, 0],
      keys:  ["i"],
      check: () => isInsert(),
    },
    {
      name: "Esc returns to NORMAL mode",
      setup: ["abc", 0, 0],
      keys:  ["i", "<Esc>"],
      check: () => isNormal(),
    },
    {
      name: "dd deletes one logical line (middle)",
      setup: ["alpha\nbeta\ngamma", 1, 0],
      keys:  ["d", "d"],
      check: () => cm.getValue() === "alpha\ngamma",
    },
    {
      name: "dd on first line",
      setup: ["alpha\nbeta\ngamma", 0, 0],
      keys:  ["d", "d"],
      check: () => cm.getValue() === "beta\ngamma",
    },
    {
      name: "yy + p duplicates current line",
      setup: ["alpha\nbeta", 0, 0],
      keys:  ["y", "y", "p"],
      check: () => cm.getValue() === "alpha\nalpha\nbeta",
    },
    {
      name: "o opens line BELOW + INSERT",
      setup: ["alpha\nbeta", 0, 0],
      keys:  ["o"],
      check: () => isInsert() && cm.getValue() === "alpha\n\nbeta",
    },
    {
      name: "O opens line ABOVE + INSERT",
      setup: ["alpha\nbeta", 1, 0],
      keys:  ["O"],
      check: () => isInsert() && cm.getValue() === "alpha\n\nbeta",
    },
    {
      name: "O on line 0 opens at top",
      setup: ["alpha\nbeta", 0, 0],
      keys:  ["O"],
      check: () => isInsert() && cm.getValue() === "\nalpha\nbeta",
    },
    {
      name: "x deletes char under cursor",
      setup: ["abcdef", 0, 2],
      keys:  ["x"],
      check: () => cm.getValue() === "abdef",
    },
    {
      name: "dw deletes word forward",
      setup: ["alpha beta gamma", 0, 0],
      keys:  ["d", "w"],
      check: () => cm.getValue() === "beta gamma",
    },
    {
      name: "0 jumps to line start",
      setup: ["alpha beta", 0, 7],
      keys:  ["0"],
      check: () => cm.getCursor().ch === 0,
    },
    {
      name: "$ jumps to line end",
      setup: ["alpha beta", 0, 0],
      keys:  ["$"],
      check: () => cm.getCursor().ch === 9,  // last char index
    },
    {
      name: "gg jumps to file start",
      setup: ["a\nb\nc", 2, 0],
      keys:  ["g", "g"],
      check: () => cm.getCursor().line === 0,
    },
    {
      name: "G jumps to file end",
      setup: ["a\nb\nc", 0, 0],
      keys:  ["G"],
      check: () => cm.getCursor().line === 2,
    },
    {
      name: "j moves down a line",
      setup: ["a\nb\nc", 0, 0],
      keys:  ["j"],
      check: () => cm.getCursor().line === 1,
    },
    {
      name: "k moves up a line",
      setup: ["a\nb\nc", 2, 0],
      keys:  ["k"],
      check: () => cm.getCursor().line === 1,
    },
    {
      name: "u undoes last change",
      setup: ["abc\ndef", 0, 0],
      keys:  ["x", "u"],
      check: () => cm.getValue() === "abc\ndef",
    },
    {
      name: "<C-r> redoes",
      setup: ["abc\ndef", 0, 0],
      keys:  ["x", "u", "<C-r>"],
      check: () => cm.getValue() === "bc\ndef",
    },
    {
      name: "/ search jumps to match",
      setup: ["alpha\nbeta\ngamma", 0, 0],
      // Search isn't a single-key sequence — uses dialog. Skip here.
      keys:  [],
      check: () => true,   // placeholder
      skip:  true,
    },
  ];

  const results = [];
  let pass = 0, fail = 0;
  for (const c of cases) {
    if (c.skip) { results.push({ name: c.name, status: "SKIP" }); continue; }
    try {
      reset(c.setup[0], c.setup[1], c.setup[2]);
      send(c.keys);
      const ok = !!c.check();
      if (ok) { pass++; results.push({ name: c.name, status: "PASS" }); }
      else {
        fail++;
        results.push({
          name:   c.name,
          status: "FAIL",
          actual: cm.getValue(),
          mode:   isInsert() ? "insert" : (cm.state.vim && cm.state.vim.visualMode ? "visual" : "normal"),
          cur:    JSON.stringify(cm.getCursor()),
        });
      }
    } catch (e) {
      fail++;
      results.push({ name: c.name, status: "FAIL", error: String(e) });
    }
  }
  // Restore editor to a clean blank state so the user can keep working.
  try { reset("", 0, 0); } catch (e) {}

  const summary = pass + " pass / " + fail + " fail (" + cases.length + " total)";
  window.__VIM_TEST_RESULTS = JSON.stringify({ summary, results }, null, 2);
  document.title = "VIMTEST " + summary;
  // Also dump into a pre at top so we can screenshot.
  let pre = document.getElementById("__vim-test-pre");
  if (!pre) {
    pre = document.createElement("pre");
    pre.id = "__vim-test-pre";
    pre.style.position = "fixed";
    pre.style.top = "0";
    pre.style.left = "0";
    pre.style.right = "0";
    pre.style.zIndex = "999999";
    pre.style.background = "#21222c";
    pre.style.color = "#f8f8f2";
    pre.style.fontSize = "12px";
    pre.style.padding = "8px";
    pre.style.fontFamily = "monospace";
    pre.style.whiteSpace = "pre-wrap";
    pre.style.maxHeight = "60vh";
    pre.style.overflow = "auto";
    document.body.appendChild(pre);
  }
  pre.textContent = window.__VIM_TEST_RESULTS;
})();
