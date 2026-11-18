"""Tab title markers: one emoji per tab mode so the user can see what each agent tab is for.

work   🤖  background work, no input needed (default)
ask    🙋  needs the user; the tab is brought to the front
scrape 🔎  read-only extraction; closed as soon as the data is out
"""
import json
import os

TAB_MODES = {"work": "\U0001F916", "ask": "\U0001F64B", "scrape": "\U0001F50E"}
DEFAULT_MODE = "work"
# Include the legacy horse so tabs marked by an older daemon get cleaned up too.
_ALL = list(TAB_MODES.values()) + ["\U0001F434"]


def enabled():
    return os.environ.get("BH_TAB_MARKER", "").strip().lower() not in {"0", "false", "no", "off"}


def _strip_js():
    return ("let t=document.title;for(const m of %s){if(t.startsWith(m+' ')){t=t.slice(m.length+1);break}}"
            % json.dumps(_ALL))


def mark_js(mode=DEFAULT_MODE):
    """Idempotent: replaces any existing marker with this mode's emoji."""
    e = json.dumps(TAB_MODES.get(mode, TAB_MODES[DEFAULT_MODE]))
    return "(()=>{%sconst n=%s+' '+t;if(document.title!==n)document.title=n})()" % (_strip_js(), e)


UNMARK_JS = "(()=>{%sif(document.title!==t)document.title=t})()" % _strip_js()
