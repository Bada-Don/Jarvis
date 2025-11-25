# Auto-reload wrapper for client.py
# Run this instead of client.py directly for auto-reload on file changes

import subprocess
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

class ClientReloader(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.restart_client()
    
    def restart_client(self):
        if self.process:
            print("\n🔄 Restarting client...")
            self.process.terminate()
            self.process.wait()
        
        print("▶️  Starting client...")
        self.process = subprocess.Popen([sys.executable, 'client.py'], cwd=os.path.dirname(__file__))
    
    def on_modified(self, event):
        if event.src_path.endswith('client.py'):
            print(f"\n📝 Detected change in {event.src_path}")
            time.sleep(0.5)  # Brief delay to ensure file is fully written
            self.restart_client()

if __name__ == '__main__':
    print("🚀 Jarvis Local Client - Auto-Reload Mode")
    print("=" * 50)
    
    event_handler = ClientReloader()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(__file__) or '.', recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    
    observer.join()
