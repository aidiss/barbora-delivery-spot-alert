import argparse
import json
import logging
import platform
import random
import sys
import time
import winsound
import requests

BEEP_FREQUENCY = 1000
BEEP_DURATION = 1000
SLEEP_RANGE = 30, 60
LOG_LEVEL = "INFO"

barbora_deliveries_url = "https://www.barbora.lt/api/eshop/v1/cart/deliveries"


def scrape_and_alarm(headers_path):
    with open(headers_path) as f:
        try:
            headers = json.load(f)
        except FileNotFoundError as e:
            logging.error(e)

    session = requests.Session()
    session.headers.update(headers)
    logging.debug(session.cookies)
    while True:
        try:
            response = session.get(barbora_deliveries_url)
            logging.debug(session.cookies)
        except requests.exceptions.RequestException as e:
            logging.error(e)
            time.sleep(random.randint(*SLEEP_RANGE))
            continue
        logging.debug(response.cookies)

        if not response.ok:
            logging.error(response.json())
            time.sleep(random.randint(*SLEEP_RANGE))

        data = response.json()
        try:
            available_hours = get_available_hours(data)
        except KeyError as e:
            logging.error(e)
            time.sleep(random.randint(*SLEEP_RANGE))
            continue

        if available_hours:
            logging("%s Open slots found!", len(available_hours))
            try:
                winsound.Beep(BEEP_FREQUENCY, BEEP_DURATION)
            except Exception as _:
                # No beep for windows
                pass
        else:
            logging.info("No open slots found")

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
    empty_count = 0
    matrix = [x["params"]["matrix"] for x in data["deliveries"]][0]
    if not matrix:
        logging.info('Empty matrix')
    for x in matrix:
        for hour in x["hours"]:
            if hour["available"]:
                available_hours.append(hour)
            else:
                empty_count += 1
    logging.info('Empty count %s', empty_count)
    return available_hours


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description="This is magic script")
    argument_parser.add_argument("command", choices=["parse_har", "alarm"])
    argument_parser.add_argument("path")
    argument_parser.add_argument("-v", "--verbose", action="store_true")
    arguments = argument_parser.parse_args()
    if arguments.verbose:
        logging.basicConfig(level='DEBUG')
    else:
        logging.basicConfig(level=LOG_LEVEL)
    path = arguments.path
    if arguments.command == "parse_har":
        har_path = path
        parse_har(har_path)
    elif arguments.command == "alarm":
        headers_path = path
        scrape_and_alarm(headers_path)
