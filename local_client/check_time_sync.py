
import time
import urllib.request
import json
from datetime import datetime

def check_time_sync():
    """
    Check the local system time against an internet time server.
    """
    try:
        print("Checking system time synchronization...")
        
        # Get local time
        local_time = time.time()
        local_dt = datetime.fromtimestamp(local_time)
        print(f"Local System Time: {local_dt}")
        
        # Get internet time (using a public API)
        url = 'https://worldtimeapi.org/api/ip'
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.load(response)
                # api returns unixtime
                server_time = data['unixtime']
                server_dt = datetime.fromtimestamp(server_time)
                
                print(f"Internet Time:     {server_dt}")
                
                offset = local_time - server_time
                print(f"Time Offset:       {offset:.2f} seconds")
                
                if abs(offset) > 30:
                    print("\n⚠️ WARNING: Your system clock is out of sync by more than 30 seconds!")
                    print("   This can cause pairing failures as tokens will appear expired.")
                    print("   Please synchronize your Windows clock in 'Date & Time settings'.")
                else:
                    print("\n✅ System time is synchronized.")
            else:
                print(f"Failed to fetch internet time: {response.status}")
            
    except Exception as e:
        print(f"Error checking time sync: {e}")

if __name__ == "__main__":
    check_time_sync()
