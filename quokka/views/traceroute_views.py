from flask import request

from quokka import app
from quokka.controller.utils import log_console
from quokka.models.apis import get_device, record_traceroute


@app.route("/traceroute/register", methods=["GET", "POST"])
def traceroute_register():

    registration_info = request.get_json()
    if not registration_info:
        return "Must provide registration information in JSON body", 404
    if "serial" not in registration_info:
        return "Must provide 'serial' in registration information", 404
    if "name" not in registration_info:
        return "Must provide 'name' in registration information", 404

    result, device = get_device(device_name=registration_info["name"])
    if result != "success":
        return "Unknown device name in registration information", 404
    if registration_info["serial"] != device["serial"]:
        return "Serial number in registration information does not match device serial", 404

    log_console(
        f"Received registration request from {registration_info['name']}, serial no: {registration_info['serial']}"
    )

    return {}, 200


@app.route("/traceroute/store", methods=["POST"])
def traceroute_store():

    traceroute_info = request.get_json()
    if not traceroute_info:
        return "Must provide traceroute information in JSON body", 404
    if "source" not in traceroute_info:
        return "Must provide 'source' in traceroute information", 404
    if "serial" not in traceroute_info:
        return "Must provide 'serial' in traceroute information", 404
    if "target" not in traceroute_info:
        return "Must provide 'target' in traceroute information", 404
    if "timestamp" not in traceroute_info:
        return "Must provide 'timestamp' in traceroute information", 404
    if "traceroute_img" not in traceroute_info:
        return "Must include 'traceroute_img' in traceroute information", 404

    record_traceroute(traceroute_info)

    log_console(
        f"Received traceroute store request from {traceroute_info['source']} for target {traceroute_info['target']}"
    )

    return {}, 200
