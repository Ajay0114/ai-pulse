import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


class ISTFormatter(logging.Formatter):
    """Logging formatter that always renders timestamps in IST,
    regardless of the host machine's own timezone."""

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc).astimezone(IST)

        if datefmt:
            return dt.strftime(datefmt)

        return dt.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logging to print IST timestamps. Only affects
    how log lines are displayed - all stored/compared timestamps in
    the application remain UTC."""

    handler = logging.StreamHandler()
    handler.setFormatter(
        ISTFormatter("%(asctime)s IST | %(levelname)s | %(message)s")
    )

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]


def to_ist(dt: datetime) -> datetime:
    """Convert a timezone-aware UTC datetime to IST for display only."""

    return dt.astimezone(IST)
