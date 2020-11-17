import pika
import json
import yaml
from quokka.controller.utils import log_console, get_this_ip

from urllib.parse import urlparse


class TracerouteManager:

    try:
        with open("quokka/data/" + "traceroutemonitors.yaml", "r") as import_file:
            traceroute_monitors = yaml.safe_load(import_file.read())
    except FileNotFoundError as e:
        log_console(f"Could not import traceroute monitors file: {repr(e)}")
        traceroute_monitors["0.0.0.0/0"] = "localhost"

    @staticmethod
    def get_channel(monitor):

        credentials = pika.PlainCredentials('quokkaUser', 'quokkaPass')
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=monitor, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue="traceroute_queue", durable=True)

        return channel

    @staticmethod
    def find_monitor(target=None):

        if not target:
            return "localhost"

        if target in TracerouteManager.traceroute_monitors:
            return TracerouteManager.traceroute_monitors[target]

        if "0.0.0.0/0" in TracerouteManager.traceroute_monitors:
            return TracerouteManager.traceroute_monitors["0.0.0.0/0"]

        # If we didn't find a specific monitor, default to localhost
        return "localhost"

    @staticmethod
    def initiate_traceroute(target, token):

        # Target could be a URL; if so, use urlparse to extract the network location (hostname)
        if target.startswith("http://") or target.startswith("https://"):
            parsed_target = urlparse(target)
            target = parsed_target.netloc

        monitor = TracerouteManager.find_monitor(target)
        channel = TracerouteManager.get_channel(monitor)

        traceroute_info = {
            "quokka": get_this_ip(),
            "target": target,
            "token": token,
        }

        traceroute_info_json = json.dumps(traceroute_info)
        channel.basic_publish(
            exchange="", routing_key="traceroute_queue", body=traceroute_info_json
        )

        log_console(
            f"Traceroute Manager: starting traceroute: target : {target}"
        )
