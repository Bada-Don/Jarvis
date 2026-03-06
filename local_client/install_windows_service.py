"""
Install JARVIS Local Client as a Windows Service
This allows the client to run in the background even when you're not logged in.
"""

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
from pathlib import Path

# Add the client directory to Python path
CLIENT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(CLIENT_DIR))


class JarvisClientService(win32serviceutil.ServiceFramework):
    _svc_name_ = "JarvisClient"
    _svc_display_name_ = "JARVIS Local Client"
    _svc_description_ = "JARVIS automation client that executes commands from the cloud backend"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_alive = True

    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False

    def SvcDoRun(self):
        """Run the service"""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()

    def main(self):
        """Main service loop"""
        try:
            # Change to client directory
            os.chdir(str(CLIENT_DIR))
            
            # Import and run the client
            import client
            client.main()
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"JARVIS Client error: {str(e)}")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(JarvisClientService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(JarvisClientService)
