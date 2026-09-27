from pathlib import Path
from gui_agent.platform.windows.window_manager import get_active_window
from gui_agent.schemas.models import WindowInfo
from mss import sct

def capture_window(window: WindowInfo, output_path: Path) -> Path:
    """Capture the visible rectangle of one validated window."""
    monitor = {
        "left": window.rect.left,
        "top": window.rect.top,
        "width": window.rect.right - window.rect.left,
        "height": window.rect.bottom - window.rect.top,
    }
    
    image = sct.grab(monitor)
    
