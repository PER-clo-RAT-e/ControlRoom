from typing import TYPE_CHECKING, Any, Callable
from dotenv import load_dotenv

load_dotenv()

if TYPE_CHECKING:
    from modules.logger import Logger

log: "Logger | None" = None

manager: Callable[..., Any] = None #type: ignore

flags = {
    'HIGHTEMP':             False,
    'HIGHTEMP++':           False,
    'LETHALTEMP':           False,
    'POWEROFF':             False,
    'MONITOR_REQUESTED':    False,
    'MONITOR_SHOWN':        False,
}

lp = 15