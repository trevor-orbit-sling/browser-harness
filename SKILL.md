---
name: browser-harness
description: "Control a real browser via CDP: clicking, typing, navigation, logged-in sessions, JS-rendered or bot-protected pages. Not for plain HTTP fetches of public content - use curl for those."
---

# browser-harness (Trevor's fork)

Direct control of Trevor's Chrome over CDP. This fork is the single source of
browser preferences; there is no separate preferences skill.

## When not to use

If a plain HTTP request can read it (public page, API, docs), use `curl` or a
fetch tool. Use the browser for interaction, a signed-in session, JS rendering,
or bot-protected pages. For public rendering or app tests that need no login,
use a separate headless Chromium with its own `--user-data-dir`, never Trevor's
live profile.

## Run

```bash
BU_CDP_URL=http://127.0.0.1:9222 BU_NAME=<task-name> browser-harness <<'PY'
tid = new_tab("https://example.com", profile="trevor@orbitsling.com")
print(page_info())
PY
```

- Helpers are pre-imported; the daemon auto-starts. Read
  `src/browser_harness/helpers.py` for the full list.
- Trevor's signed-in Chrome is the one on port 9222 (user data dir
  `~/.config/google-chrome-remote-debug`). Other Chrome processes are task
  browsers or app shells; ignore them unless you launched them.
- Use a short task-specific `BU_NAME` and keep it for the whole task. Each daemon
  has one attached tab, so parallel agents must not share a name. Daemons exit
  after 30 idle minutes (`BH_DAEMON_IDLE`).
- First navigation is `new_tab(...)`; later calls stay on the attached tab.
- Browser calls time out after 30s (`BH_IPC_TIMEOUT`). Gmail, Google Admin
  and Docs work at this setting, so there is no need to fall back to Playwright.

## Pick the profile, then prove it

- Decide which account the task needs before opening anything.
  `profiles()` lists the open profiles (`dir`, `name`, `email`). Pass
  `profile=` (an email, name, or dir like `"Profile 1"`) to `new_tab`/`scrape`.
  Without it, Chrome picks a profile arbitrarily. Ask only if the account is
  genuinely ambiguous.
- Google URLs like `/mail/u/0/` are per profile, so `u/0` differs between profiles.
  Never trust an index or `authuser=`.
- Before any write (send, save, post, edit), assert the signed-in identity from
  the page itself (Gmail `document.title` holds the address; the Admin console
  header; the LinkedIn profile name). Abort if it doesn't match. Check the
  precondition, e.g. "the editor still holds the old text", before overwriting.
- Landing on `accounts.google.com/.../signin` means that profile's session
  expired. Stop and tell Trevor which profile; he has 2FA.
- For authorized setup work, complete ordinary SSO and device-authorization flows in
  the verified profile yourself, rather than handing Trevor a code. Stop for
  passwords, MFA, consent beyond the task, or an ambiguous identity.

## Tabs: three modes

Every tab you open carries an emoji in its title so Trevor can see what it is for.

| Mode | Emoji | Use | Visible? |
|---|---|---|---|
| `work` (default) | 🤖 | anything that doesn't need Trevor | background |
| `ask` | 🙋 | Trevor must log in, approve, choose, or look | brought to front |
| `scrape` | 🔎 | read-only extraction | background, closed right after |

```python
with scrape(url, profile="saqikawaay@gmail.com"):   # closes even on error
    rows = js("[...document.querySelectorAll('tr')].map(r => r.innerText)")

tid = new_tab(url, profile="Profile 4")              # 🤖 background work
set_tab_mode("ask", tid)                             # 🙋 needs Trevor: comes to front
set_tab_mode("work", tid)                            # back to 🤖 once he's done
cleanup()                                            # end of every task, in a finally
```

- `cleanup()` closes every tab this daemon opened, plus popups they spawned. It
  never touches Trevor's own tabs, and it keeps 🙋 tabs unless `include_ask=True`.
  Use `keep=[tid]` for a tab he asked to keep or one holding unsaved work.
- Only `ask` takes focus. Never call `activate_tab`, `Page.bringToFront`, or raise
  windows otherwise. Screenshots, DOM reads and CDP input all work in background
  tabs. If a page pauses while hidden, wrap the step in
  `cdp("Emulation.setFocusEmulationEnabled", enabled=True)` / `False`.
- Attaching to one of Trevor's existing tabs (`switch_tab`) is fine for reading.
  Don't navigate it away or close it.

## Page workflow

- Find elements with the accessibility tree, not screenshots:
  `cdp("Accessibility.getFullAXTree")["nodes"]`. Filter in Python before
  printing. Get the centre with `DOM.getBoxModel(backendNodeId=...)`, then
  `click_at_xy(x, y)`, then verify with `js(...)` or `page_info()`.
- `wait_for_load()` after navigation; `wait_for_element(sel)` for late content.
- Use `js(...)` for extraction. Use `fill_input`, `type_text` and `press_key` for
  input; they send real key codes. Raw CDP: `cdp("Domain.method", ...)`.
- Screenshot only when layout or images matter.

## Gmail

- Hash navigation (`#settings/general`) doesn't reload the app. For a real
  reload, `goto_url` the base `/mail/u/N/`, then the hash. "Save Changes" itself
  reloads to `#inbox`.
- A new signature exists only after "Save Changes". Verify after a real reload,
  and in a fresh Compose window with the right From address.
- The Gmail API can't set a signature on a non-primary alias without domain-wide
  delegation. Use the settings UI.
- Discard compose drafts you opened (`[aria-label*='Discard draft']`).

## Reference

Recipes for tricky mechanics (iframes, shadow DOM, uploads, downloads, dialogs,
dropdowns, scrolling, cookies, network capture, PDFs) are in
`~/browser-harness/interaction-skills/`. Read one only when you're stuck on that
mechanic. `browser-harness --doctor` diagnoses connection problems.
Cloud browsers, recordings and domain skills exist upstream but aren't part of
Trevor's workflow. Don't suggest them, and never send Browser Use feedback or
open PRs to `browser-use/browser-harness`.
