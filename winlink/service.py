import subprocess
import win32event
import win32file
import win32pipe
import win32service
import win32serviceutil

BUFFER_SIZE = 4096


class SymlinkService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'SymlinkService'
    _svc_display_name_ = 'Python Symlink Service'
    _svc_description_ = "Python Service to create symlinks via named pipes"

    def __init__(self, *args, **kwargs):
        win32serviceutil.ServiceFramework.__init__(self, *args, **kwargs)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def symlink(self, link, target, hardlink=False):
        command = "cmd /c mklink "
        if hardlink:
            command = command + "/h "
        command = command + link + " " + target
        subprocess.call(command, shell=False)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        #import servicemanager
        #servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED,
        #                      (self._svc_name_, ''))

        hPipe = win32pipe.CreateNamedPipe(
            "\\\\.\\pipe\\symlink",
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,  # TODO win32pipe.PIPE_REJECT_REMOTE_CLIENTS
            1,
            BUFFER_SIZE,
            BUFFER_SIZE,
            0,
            None,
        )

        if hPipe is None or hPipe == win32file.INVALID_HANDLE_VALUE:
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)
            return

        timeout = 50

        while True:
            # check to see if self.hWaitStop happened
            rc = win32event.WaitForSingleObject(self.hWaitStop, timeout)
            if rc == win32event.WAIT_OBJECT_0:
                self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
                break

            # check for client
            win32pipe.DisconnectNamedPipe(hPipe)
            connected = win32pipe.ConnectNamedPipe(hPipe, None)
            if not connected:
                continue

            # TODO read paths and create link

        win32file.CloseHandle(hPipe)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(SymlinkService)
