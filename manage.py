import subprocess
import time
import os


while True:
    if os.path.exists('lockfile'):
        continue
    subprocess.call('запуск.bat')
    time.sleep(10)
    