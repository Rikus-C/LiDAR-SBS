import time
import subprocess

while True:
    print("starting application")
    # Wait for the target script to exit
    process = subprocess.Popen(
        ["python", "./main.py"], shell = True)
    process.wait()  

    # Wait for 0.5 seconds before restarting
    time.sleep(0.5) 