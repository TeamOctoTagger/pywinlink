import winerror
import win32api
import win32file
import win32pipe

from . import service


def symlink(source, link_name, hardlink=False):
    # connect to pipe
    while True:
        pipe = win32file.CreateFile(
            service.PIPE_NAME,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0,
            None,
            win32file.OPEN_EXISTING,
            win32file.FILE_ATTRIBUTE_NORMAL,
            None,
        )

        if pipe != win32file.INVALID_HANDLE_VALUE:
            # connection established
            break

        if win32api.GetLastError() != winerror.ERROR_PIPE_BUSY:
            raise IOError("Could not open pipe")

        if not win32pipe.WaitNamedPipe(
            service.PIPE_NAME,
            win32pipe.NMPWAIT_USE_DEFAULT_WAIT
        ):
            raise IOError("Pipe not available")

    # TODO write paths
    print("Works!")

    # disconnect from pipe
    win32file.CloseHandle(pipe)
