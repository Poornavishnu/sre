import psutil
import shutil
import subprocess
import sys


class SystemCapabilities:
    def __init__(self):
        self.capabilities = {
            "cpu": True,
            "memory": True,
            "disk": True,
            "temperature": False,
            "battery": False,
            "gpu": False
        }

    def detect(self):
        self._check_cpu()
        self._check_memory()
        self._check_disk()
        self._check_temperature()
        self._check_battery()
        self._check_gpu()
        return self.capabilities

    def _check_cpu(self):
        try:
            psutil.cpu_percent()
        except Exception:
            self.capabilities["cpu"] = False

    def _check_memory(self):
        try:
            psutil.virtual_memory()
        except Exception:
            self.capabilities["memory"] = False

    def _check_disk(self):
        try:
            psutil.disk_usage("/")
        except Exception:
            self.capabilities["disk"] = False

    def _check_temperature(self):
        try:
            temps = psutil.sensors_temperatures()
            if temps and any(temps.values()):
                self.capabilities["temperature"] = True
        except Exception:
            self.capabilities["temperature"] = False

    def _check_battery(self):
        try:
            batt = psutil.sensors_battery()
            if batt is not None:
                self.capabilities["battery"] = True
        except Exception:
            self.capabilities["battery"] = False

    def _check_gpu(self):
        try:
            result = subprocess.run(["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                self.capabilities["gpu"] = True
        except FileNotFoundError:
            self.capabilities["gpu"] = False


if __name__ == "__main__":
    print("Checking system...")

    if not shutil.which("python3"):
        print("Python 3 not found!")
        sys.exit(1)

    try:
        import psutil  # Reconfirm for CLI
    except ImportError as e:
        print(f"Missing Python dependency: {e}")
        sys.exit(1)

    print("Python dependencies found.")
    detector = SystemCapabilities()
    print("Detected capabilities:")
    print(detector.detect())