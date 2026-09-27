from dataclasses import dataclass

@dataclass
class Rect:
    left: int
    top: int
    right: int
    bottom: int

    @property
    def center(self) -> tuple[int, int]:
        return (
            (self.left + self.right) // 2,
            (self.top + self.bottom) // 2,
        )
        
@dataclass
class WindowInfo:
    handle: int
    title: str
    process_id: int
    class_name: str
    rect: Rect
    is_foreground: bool