import winerror
import win32api
import win32file
import win32pipe

from . import service


def symlink(source, link_name, hardlink=False):
    while True:
        try:
            pipe = win32file.CreateFile(
                service.PIPE_NAME,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                win32file.FILE_ATTRIBUTE_NORMAL,
                None,
            )
        except win32api.error as e:
            if e[0] == 2:
                # The system cannot find the file specified
                raise IOError("Could not find pipe")
            elif e[0] == 231:
                # All pipe instances are busy
                pass
            else:
                raise

        if pipe != win32file.INVALID_HANDLE_VALUE:
            # connection established
            break

        if win32api.GetLastError() != winerror.ERROR_PIPE_BUSY:
            raise IOError("Could not open pipe")

        if not win32pipe.WaitNamedPipe(
            service.PIPE_NAME,
            win32pipe.NMPWAIT_USE_DEFAULT_WAIT
        ):
            raise IOError("Pipe is busy")

    try:
        (error, bytes_written) = win32file.WriteFile(pipe, source)
        if error:
            raise IOError("Could not write source path to service")

        (error, bytes_written) = win32file.WriteFile(pipe, link_name)
        if error:
            raise IOError("Could not write link path to service")

        (error, bytes_written) = win32file.WriteFile(pipe, str(hardlink))
        if error:
            raise IOError("Could not write link type to service")

        (error, result) = win32file.ReadFile(pipe, service.BUFFER_SIZE)
        if error:
            raise IOError("Could not read from service")

        if result == "success":
            return
        elif result.startswith("error:"):
            error = result.split(":")[1]
            raise IOError(error)
        else:
            raise IOError("Got unexpected response from service")
    except win32api.error as e:
        if e[0] == 109:
            # The pipe has been ended
            raise IOError("Service closed unexpectedly")
    finally:
        win32file.CloseHandle(pipe)
