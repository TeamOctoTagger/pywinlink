import winerror
import win32api
import win32file
import win32pipe
import win32security
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

    def symlink(self, link, target, hardlink):
        # TODO ensure source and link_name are real paths
        if hardlink:
            win32file.CreateHardLink(link, target)
        else:
            win32file.CreateSymbolicLink(link, target)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False

    def SvcDoRun(self):
        sa = win32security.SECURITY_ATTRIBUTES()
        sa.SECURITY_DESCRIPTOR.SetDacl(True, None, False)

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
            sa,
        )

        if pipe == win32file.INVALID_HANDLE_VALUE:
            raise IOError("Could not create pipe", win32api.GetLastError())

        while self.running:
            win32api.Sleep(SLEEP_TIME)

            try:
                # connect to a new client
                connected = (
                    win32pipe.ConnectNamedPipe(pipe, None) != 0 or
                    win32api.GetLastError() == winerror.ERROR_SUCCESS or
                    win32api.GetLastError() == winerror.ERROR_PIPE_CONNECTED
                )
                if not connected:
                    continue

                (error, target) = win32file.ReadFile(pipe, BUFFER_SIZE)
                if error or len(target) == 0:
                    continue

                (error, link) = win32file.ReadFile(pipe, BUFFER_SIZE)
                if error or len(link) == 0:
                    continue

                (error, hardlink) = win32file.ReadFile(pipe, BUFFER_SIZE)
                if error or len(link) == 0:
                    continue

                self.symlink(link, target, hardlink == "True")

                win32file.WriteFile(pipe, "done")  # TODO better

                win32file.FlushFileBuffers(pipe)
                win32pipe.DisconnectNamedPipe(pipe)
            except win32api.error as e:
                if e[0] == 536:
                    # pipe waiting for other end to be opened
                    continue
                raise

        win32file.CloseHandle(pipe)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)


def main():
    win32serviceutil.HandleCommandLine(SymlinkService)


if __name__ == '__main__':
    main()
