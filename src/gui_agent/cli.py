import argparse

from gui_agent.platform.windows.window_manager import get_active_window

def main():
    parser = argparse.ArgumentParser(
        prog="gui-agent",
        description="Inspect and interact with Windows GUI applications.",
    )
    
    parser.add_argument(
        "test",
        choices=("test",),
        help="Print information about the currently active window.",
    )
    
    args = parser.parse_args()

    if args.test == "test":
        print(get_active_window())
