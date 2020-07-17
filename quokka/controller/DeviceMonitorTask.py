import socket
from datetime import datetime

from time import sleep

from quokka.controller.device.device_status import get_device_status
from quokka.models.apis import get_all_devices, set_device, record_device_status, log_event
from quokka.controller.utils import log_console


def calculate_cpu(cpu):

    num_cpus = 0
    cpu_total = 0.0
    for cpu, usage in cpu.items():
        cpu_total += usage["%usage"]
        num_cpus += 1

    return int(cpu_total / num_cpus)


def calculate_memory(memory):

    return int((memory["used_ram"] * 100) / memory["available_ram"])


class DeviceMonitorTask:

    def __init__(self):
        self.terminate = False

    def set_terminate(self):
        if not self.terminate:
            self.terminate = True
            log_console(f"{self.__class__.__name__}: monitor:device Terminate pending")

    def monitor(self, interval):

        while True and not self.terminate:

            devices = get_all_devices()
            log_console(f"Monitor: Beginning monitoring for {len(devices)} devices")
            for device in devices:

                try:
                    ip_address = socket.gethostbyname(device["hostname"])
                except (socket.error, socket.gaierror) as e:
                    info = f"!!! Caught socket error {repr(e)}, continuing to next device"
                    log_console(info)
                    log_event(str(datetime.now())[:-3], "device", device['name'], "SEVERE", info)
                    ip_address = None

                if self.terminate:
                    break

                log_console(f"--- monitor:device get environment {device['name']}")
                device_status = get_device_status(device)

                device["ip_address"] = ip_address
                device["availability"] = device_status["availability"]
                device["response_time"] = device_status["response_time"]
                device["cpu"] = device_status["cpu"]
                device["memory"] = device_status["memory"]

                if device_status["last_heard"]:
                    device["last_heard"] = device_status["last_heard"]

                record_device_status(device)
                set_device(device)

            for _ in range(0, int(interval / 10)):
                sleep(10)
                if self.terminate:
                    break

        log_console("...gracefully exiting monitor:device")
