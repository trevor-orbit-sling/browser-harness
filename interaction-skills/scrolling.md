# Scrolling

Separate page scroll, nested containers, virtualized lists, and dropdown menus, and identify which element is actually consuming wheel events before scrolling.

## Hidden tabs

`scroll(...)` works in background tabs: it turns on focus emulation for the tab
first (Chrome otherwise never answers a wheel event in a hidden tab) and leaves
it on, because switching it off right away defers the scroll. Never call
`activate_tab()` to scroll.

If background scrolling still fails, stop and name that exact limitation.
Call `activate_tab()` only when the user explicitly asks to see or visibly
switch to the tab. Do not replace wheel input with custom `Runtime.evaluate`
scrolling or a cross-frame JavaScript walker; those paths change page semantics
and require context the agent does not have.
