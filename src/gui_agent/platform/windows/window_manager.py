import win32gui
import win32process
from gui_agent.schemas.models import WindowInfo, Rect

def get_active_window():
    handle = win32gui.GetForegroundWindow()
    
    if not handle:
        raise RuntimeError("No active window found")
    
    title = win32gui.GetWindowText(handle)
    left, top, right, bottom = win32gui.GetWindowRect(handle)
    class_name = win32gui.GetClassName(handle)
    process_id = win32process.GetWindowThreadProcessId(handle)[1]
    
    return WindowInfo(
        handle=handle,
        title=title,
        process_id=process_id,
        class_name=class_name,
        rect=Rect(left, top, right, bottom),
        is_foreground=True,
    )

