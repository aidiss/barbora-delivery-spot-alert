import argparse
import json
import platform
import random
import sys
import time
from datetime import datetime
import winsound
import requests

BEEP_FREQUENCY = 1000
BEEP_DURATION = 1000
SLEEP_RANGE = 30, 60

barbora_deliveries_url = "https://www.barbora.lt/api/eshop/v1/cart/deliveries"


def scrape_and_alarm(headers_path):
    with open(headers_path) as f:
        try:
            headers = json.load(f)
        except FileNotFoundError as e:
            print(e)

    while True:
        try:
            response = requests.get(barbora_deliveries_url, headers=headers)
        except requests.exceptions.RequestException as e:
            print(e)
            time.sleep(random.randint(*SLEEP_RANGE))
            continue

        if not response.ok:
            print(response.json())
            time.sleep(random.randint(*SLEEP_RANGE))

        data = response.json()
        available_hours = get_available_hours(data)
        if available_hours:
            print('found')
            try:
                winsound.Beep(BEEP_FREQUENCY, BEEP_DURATION)
            except Exception as _:
                # No beep for windows
                pass

        now = datetime.now()
        print(now)

        time.sleep(random.randint(*SLEEP_RANGE))


def parse_har(path):
    assert "har" in path
    with open(path, encoding="utf8") as f:
        data = json.load(f)

    headers = get_delivieries_headers(data)

    if headers:
        output_filename = path + ".json"
        with open(output_filename, "w") as f:
            json.dump(headers, f, indent=4)


def get_delivieries_headers(data):
    for entry in data["log"]["entries"]:
        request = entry["request"]
        url = request["url"]
        if "deliveries" in url:
            headers = {header["name"]: header["value"] for header in request["headers"]}
            return headers


def get_available_hours(data):
    available_hours = []
    matrix = [x["params"]["matrix"] for x in data["deliveries"]][0]
    for x in matrix:
        for hour in x["hours"]:
            if hour["available"]:
                available_hours.append(hour)
    return available_hours


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description="This is magic script")
    argument_parser.add_argument("command", choices=["parse_har", "alarm"])
    argument_parser.add_argument("path")
    arguments = argument_parser.parse_args()
    path = arguments.path
    if arguments.command == "parse_har":
        har_path = path
        parse_har(har_path)
    elif arguments.command == "alarm":
        headers_path = path
        scrape_and_alarm(headers_path)
