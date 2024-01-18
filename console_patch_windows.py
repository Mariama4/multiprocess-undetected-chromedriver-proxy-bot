import ctypes


# Constants
STD_INPUT_HANDLE = -10


# Enum for ConsoleModes
class ConsoleModes(ctypes.c_uint):
    ENABLE_PROCESSED_INPUT = 0x1
    ENABLE_LINE_INPUT = 0x2
    ENABLE_ECHO_INPUT = 0x4
    ENABLE_WINDOW_INPUT = 0x8
    ENABLE_MOUSE_INPUT = 0x10
    ENABLE_INSERT_MODE = 0x20
    ENABLE_QUICK_EDIT_MODE = 0x40
    ENABLE_EXTENDED_FLAGS = 0x80
    ENABLE_AUTO_POSITION = 0x100


# Import kernel32.dll functions
kernel32 = ctypes.windll.kernel32
GetStdHandle = kernel32.GetStdHandle
GetConsoleMode = kernel32.GetConsoleMode
SetConsoleMode = kernel32.SetConsoleMode


def disable_quick_edit_mode():
    std_in = GetStdHandle(STD_INPUT_HANDLE)
    mode = ctypes.c_uint()
    if GetConsoleMode(std_in, ctypes.byref(mode)):
        if mode.value & ConsoleModes.ENABLE_QUICK_EDIT_MODE:
            mode.value ^= ConsoleModes.ENABLE_QUICK_EDIT_MODE
            SetConsoleMode(std_in, mode)