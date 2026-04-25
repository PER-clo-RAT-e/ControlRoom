from modules.instancer import manager
import modules.instancer as instancer

import psutil
import time
import subprocess

assert instancer.log is not None
log = instancer.log

flags = instancer.flags

class SafetyManager:
    @manager
    def __init__(self) -> None:
        self.temperatures = psutil.sensors_temperatures()
        self.run = True
        self.path = "/sys/devices/system/cpu/intel_pstate/max_perf_pct"

        self.lifepower = 15.0
        
        try:
            with open(self.path, 'r') as f:
                self.original_perf = f.read().strip()
        except Exception as e:
            self.original_perf = "100"
            log.warn('Error when reading perf. Using default `100`', str(e))

    def set_cpu_power(self, percent: int):
        try:
            subprocess.run(
                ['sudo', '/usr/bin/tee', self.path],
                input=str(percent).encode(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                check=True
            )
        except subprocess.CalledProcessError as e:
            log.error(f"Safety: Subprocess error! Code: {e.returncode}", str(e.stderr))
        except Exception as e:
            log.error(f"Safety: Failed to set power to {percent}%", str(e))


    def restore_and_exit(self):
        log.info(f"Safety: Restoring CPU power to {self.original_perf}%")
        self.set_cpu_power(int(self.original_perf))
        self.run = False

    def cycle(self):
        while self.run:
            self.temperatures = psutil.sensors_temperatures()
            cpu_temp = self.temperatures['coretemp'][0].current
            if cpu_temp >= 98:
                self.lifepower = max(-2.1, self.lifepower - 0.8)

            elif 98 > cpu_temp > 75:
                self.lifepower = max(2, self.lifepower - 0.3)

            elif 75 > cpu_temp > 60:
                self.lifepower = min(20, self.lifepower + 0.1)

            elif cpu_temp < 60:
                self.lifepower = min(20, self.lifepower + 0.3)
            
            

            if self.lifepower > 15:
                flags['HIGHTEMP'] = False
                flags['HIGHTEMP++'] = False
                flags['LETHALTEMP'] = False
                flags['POWEROFF'] = False
            
            if self.lifepower < 10:
                flags['HIGHTEMP'] = True
            
            if self.lifepower < 2:
                flags['HIGHTEMP++'] = True

            if self.lifepower < 0:
                flags['LETHALTEMP'] = True

            if self.lifepower < -2.0:
                flags['POWEROFF'] = True

            instancer.lp = self.lifepower

            time.sleep(0.3)