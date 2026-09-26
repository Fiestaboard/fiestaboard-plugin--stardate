"""Stardate plugin for FiestaBoard.

Displays the current TNG-style stardate.
"""

from typing import Any, Dict, List, Optional
import logging
from datetime import datetime
import calendar
import pytz

from src.devices import BoardContext
from src.plugins.base import PluginBase, PluginResult

logger = logging.getLogger(__name__)

# self.board is None outside a board-scoped render (unit tests, legacy
# callers). Treat that as "assume a Flagship" rather than crashing -- this is
# the only dimension literal in the module, and it exists solely as the
# default for an *unbound* board, never as a layout constant.
_DEFAULT_BOARD = BoardContext(device_type="flagship", rows=6, cols=22)


class StardatePlugin(PluginBase):
    """Stardate plugin.

    Provides the current TNG-era stardate.
    """

    def __init__(self, manifest: Dict[str, Any]):
        """Initialize the stardate plugin."""
        super().__init__(manifest)

    @property
    def plugin_id(self) -> str:
        return "stardate"

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate stardate configuration."""
        errors = []

        timezone = config.get("timezone", "America/Los_Angeles")
        try:
            pytz.timezone(timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            errors.append(f"Invalid timezone: {timezone}")

        return errors

    def fetch_data(self) -> PluginResult:
        """Fetch current stardate using canonical TNG formula.

        TNG stardate system: Stardate 0 = 2323-01-01
        Each year = 1000 stardate units
        Formula: (Year - 2323) × 1000 + (day_of_year / days_in_year × 1000)

        Present day (2020s) will have negative stardates since we're
        in the 24th century's past.
        """
        try:
            timezone_str = self.config.get("timezone", "America/Los_Angeles")
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)

            days_in_year = 366 if calendar.isleap(now.year) else 365
            day_fraction = now.timetuple().tm_yday / days_in_year
            stardate_value = (now.year - 2323) * 1000 + (day_fraction * 1000)

            stardate = f"{stardate_value:.1f}"

            return PluginResult(
                available=True,
                data={"stardate": stardate},
                formatted_lines=self._build_lines(stardate),
            )

        except Exception as e:
            logger.exception("Error fetching stardate")
            return PluginResult(
                available=False,
                error=str(e)
            )

    def _build_lines(self, stardate: str) -> List[str]:
        """Lay out the label and value for the current board, whatever its size.

        This plugin has exactly two lines of content -- a label and a
        value -- on every board. There is nothing to reflow into a list, so
        the fix here is to derive width from the board and centre the two
        lines vertically within its height, rather than the previous fixed
        6-row/22-col literal. Growth (more rows) is deliberately spent as
        centring whitespace, not invented filler content.
        """
        board = self.board or _DEFAULT_BOARD
        rows, cols = board.rows, board.cols

        content = ["STARDATE".center(cols), stardate.center(cols)]

        padding = max(rows - len(content), 0)
        top_padding = padding // 2
        bottom_padding = padding - top_padding

        lines = ([""] * top_padding) + content + ([""] * bottom_padding)
        # Defensive only: every real board is at least 3 rows tall (the
        # narrowest Note), so this never actually truncates content.
        return lines[:rows]

    def get_formatted_display(self) -> Optional[List[str]]:
        """Return default formatted stardate display."""
        result = self.fetch_data()
        if not result.available or not result.data:
            return None

        return result.formatted_lines or self._build_lines(result.data["stardate"])


# Export the plugin class
Plugin = StardatePlugin
