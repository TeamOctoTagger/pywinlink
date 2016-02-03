import os
import sys
import win32serviceutil
import win32service
import win32event
import win32api
import win32file
import win32pipe

def symlink(source, link_name, hardlink=False):
    hPipe = win32file.CreateFile(
        "\\\\.\\pipe\\symlink",
        win32file.GENERIC_READ,  # | win32file.GENERIC_WRITE,
        0,
        None,
        win32file.OPEN_EXISTING,
        win32file.FILE_ATTRIBUTE_NORMAL,
        None,
    )

    if hPipe is None or hPipe == win32file.INVALID_HANDLE_VALUE:
        print("Error!")
        raise None  # TODO handle missing pipe

    # TODO write paths
    print("Works!")

    win32file.CloseHandle(hPipe)