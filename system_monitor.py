import psutil
import logging
from datetime import datetime
import speedtest
import subprocess
import time
import ntplib
from time import ctime

class SystemMonitor:
    def __init__(self):
        self.boot_time = datetime.fromtimestamp(psutil.boot_time())
        self.ntp_server = '46.188.50.48'

    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=1)

    def get_memory_usage(self):
        mem = psutil.virtual_memory()
        return {
            'total_mb': round(mem.total / (1024**2), 2),
            'used_mb': round(mem.used / (1024**2), 2),
            'available_mb': round(mem.available / (1024**2), 2),
            'percent': mem.percent
        }

    def get_uptime(self):
        uptime = datetime.now() - self.boot_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}д {hours}ч {minutes}м {seconds}с"

    def test_internet_speed(self):
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            download = st.download() / 1_000_000
            upload = st.upload() / 1_000_000
            ping = st.results.ping
            return {'download': round(download, 2), 'upload': round(upload, 2), 'ping': round(ping, 2)}
        except Exception as e:
            logging.error(f"Ошибка теста скорости: {e}")
            return None

    def get_ntp_time(self):
        try:
            client = ntplib.NTPClient()
            response = client.request(self.ntp_server, version=3)
            return ctime(response.tx_time)
        except Exception as e:
            logging.error(f"Ошибка получения времени с NTP: {e}")
            return None

    def get_system_stats(self):
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_usage': self.get_cpu_usage(),
            'memory': self.get_memory_usage(),
            'uptime': self.get_uptime(),
            'boot_time': self.boot_time.isoformat(),
            'server_time': self.get_ntp_time()
        }

    def check_alerts(self, stats, thresholds):
        alerts = []
        if stats['cpu_usage'] > thresholds['cpu']:
            alerts.append(f"Высокая загрузка CPU: {stats['cpu_usage']}%")
        if stats['memory']['percent'] > thresholds['ram']:
            alerts.append(f"Высокое использование RAM: {stats['memory']['percent']}%")
        return alerts
