"""Board-geometry conformance for the stardate plugin.

Stardate needs no network access -- fetch_data reads the local clock -- so
``make_plugin`` just returns a configured instance directly; there is nothing
to stub.

``strict_growth`` is deliberately omitted (left False): this plugin has
exactly two lines of content (a label and a value) on every board. A taller
board is not supposed to grow more rows of *content* -- it is supposed to
centre those same two lines in more whitespace -- so the "taller board must
render strictly more rows once full" rule would punish the correct behavior
here. See ``_build_lines`` in ``__init__.py``.
"""

import json
from pathlib import Path

from src.plugins.geometry_conformance import assert_board_conformance

from plugins.stardate import StardatePlugin

MANIFEST = json.loads((Path(__file__).parent.parent / "manifest.json").read_text())


def make_plugin() -> StardatePlugin:
    """Fresh, ready-to-render plugin. No network access is involved."""
    plugin = StardatePlugin(MANIFEST)
    plugin.config = {"enabled": True, "timezone": "America/Los_Angeles"}
    return plugin


def test_renders_on_every_board_shape():
    assert_board_conformance(
        make_plugin,
        manifest=MANIFEST,
        strict_growth=False,  # two fixed lines of content; see module docstring
        require_note_array_preview=True,
    )
