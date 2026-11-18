import shutil, subprocess

import pytest

from browser_harness import markers


def _run(js_body):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    return subprocess.run([node, "-e", js_body], capture_output=True, text=True, check=True).stdout.strip()


@pytest.mark.parametrize("start", ["Inbox", "\U0001F434 Inbox", "\U0001F916 Inbox", "\U0001F50E Inbox"])
def test_mark_replaces_any_marker_and_unmark_restores(start):
    js = f"""
    globalThis.document = {{title: {start!r}}};
    {markers.mark_js("ask")};
    const a = document.title;
    {markers.mark_js("ask")};
    const b = document.title;
    {markers.UNMARK_JS};
    console.log(JSON.stringify([a, b, document.title]));
    """
    import json
    a, b, plain = json.loads(_run(js))
    assert a == b == "\U0001F64B Inbox"
    assert plain == "Inbox"


def test_unknown_mode_falls_back_to_work():
    assert "\\ud83e\\udd16" in markers.mark_js("nope")
