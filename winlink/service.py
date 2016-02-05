import winerror
import win32api
import win32file
import win32pipe
import win32service
import win32serviceutil

PIPE_NAME = r'\\.\pipe\symlink'
BUFFER_SIZE = 4096
SLEEP_TIME = 50


class SymlinkService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'SymlinkService'
    _svc_display_name_ = 'Python Symlink Service'
    _svc_description_ = "Python Service to create symlinks via named pipes"

    def __init__(self, *args, **kwargs):
        win32serviceutil.ServiceFramework.__init__(self, *args, **kwargs)
        self.running = True

    def symlink(self, link, target, hardlink=False):
        if hardlink:
            win32file.CreateHardLink(link, target)
        else:
            win32file.CreateSymbolicLink(link, target)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False

    def SvcDoRun(self):
        pipe = win32pipe.CreateNamedPipe(
            PIPE_NAME,
            win32pipe.PIPE_ACCESS_DUPLEX,
            (
                win32pipe.PIPE_TYPE_MESSAGE |
                win32pipe.PIPE_READMODE_MESSAGE |
                win32pipe.PIPE_NOWAIT
                # TODO win32pipe.PIPE_REJECT_REMOTE_CLIENTS
            ),
            1,
            BUFFER_SIZE,
            BUFFER_SIZE,
            0,
            None,
        )

        if pipe == win32file.INVALID_HANDLE_VALUE:
            raise IOError("Could not create pipe", win32api.GetLastError())

        while self.running:
            win32api.Sleep(SLEEP_TIME)

            try:
                # make sure no client is connected
                win32pipe.DisconnectNamedPipe(pipe)

                # connect to a new client
                connected = (
                    win32pipe.ConnectNamedPipe(pipe, None) or
                    win32api.GetLastError() == winerror.ERROR_PIPE_CONNECTED
                )
                if not connected:
                    continue

                # TODO read paths and create link
            except win32api.error:
                continue

        win32file.CloseHandle(pipe)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(SymlinkService)
