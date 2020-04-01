import argparse
import json
import logging
import platform
import random
import sys
import time

import requests

from utils import HTTPRequest

PLATFORM = "WIN"

if platform.system().lower().startswith('win'):
    import winsound
elif platform.system().lower().startswith('dar'):
    import os
    PLATFORM = "MAC"

BEEP_FREQUENCY = 1000
BEEP_DURATION = 1000
SLEEP_RANGE = 30, 60
COOKIES_PATH = "cookies.json"
LOG_LEVEL = "INFO"

barbora_deliveries_url = "https://www.barbora.lt/api/eshop/v1/cart/deliveries"


def scrape_and_alarm(headers_path):
    headers = {}
    with open(headers_path) as f:
        try:
            headers = json.load(f)
            logger.info("Loaded headers")
        except FileNotFoundError as e:
            logger.error(e)

    cookies = {}

    try:
        with open(COOKIES_PATH) as f:
            cookies = json.load(f)
            logger.info(
                "Loaded cookies from %s. Delete file if you do not want to use most recent cookies",
                COOKIES_PATH,
            )
    except FileNotFoundError as _:
        pass
    except json.decoder.JSONDecodeError as _:
        print("file")

    session = requests.Session()
    session.headers.update(headers)

    while True:
        try:
            response = session.get(barbora_deliveries_url, cookies=cookies)
            logger.debug(session.cookies)
            with open(COOKIES_PATH, "w") as f:
                try:
                    json.dump(dict(session.cookies), f, indent=4)
                except FileNotFoundError as e:
                    logger.error(e)

        except requests.exceptions.RequestException as e:
            logger.error(e)
            time.sleep(random.randint(*SLEEP_RANGE))
            continue
        logger.debug(response.cookies)

        if not response.ok:
            logger.error(response.status_code)
            time.sleep(random.randint(*SLEEP_RANGE))
            continue

        data = response.json()
        try:
            slots = get_available_hours(data)
        except KeyError as e:
            logger.error(e)
            time.sleep(random.randint(*SLEEP_RANGE))
            continue

        if slots["available"]:
            logger.info("%s Open slots found!", len(slots["available"]))
            for slot in slots['available']:
                logger.info('%s  %s', slot['deliveryTime'], slot['hour'])
            try:
                if PLATFORM == "WIN":
                    winsound.Beep(BEEP_FREQUENCY, BEEP_DURATION)
                elif PLATFORM == "MAC":
                    os.system('say "Open slots found"')
            except Exception as _:
                # No beep for windows
                # Beep for Linux ALSA
                import os
                os.system("speaker-test -t sine -f 1000 -l 1 & sleep .9 && kill -9 $!")
                pass

        logger.info(
            "%s open and %s closed slots",
            len(slots["available"]),
            len(slots["not_available"]),
        )

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

def parse_headers(path):
    with open(path) as f:
        data = f.read()

    request = HTTPRequest(data)

    headers = dict(request.headers)

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
    slots = {"available": [], "not_available": []}

    matrix = [x["params"]["matrix"] for x in data["deliveries"]][0]
    for x in matrix:
        for hour in x["hours"]:
            if hour["available"]:
                slots["available"].append(hour)
            else:
                slots["not_available"].append(hour)

    return slots

def magic():
    # load headers
    headers_path = 'headers.json'
    with open(headers_path) as f:
        headers = json.load(f)
    session = requests.Session()
    session.headers.update(headers)
    response = session.get(barbora_deliveries_url)
    data = response.json()
    slots = get_available_hours(data)
    report = "%s open and %s closed slots" % (len(slots["available"]), len(slots["not_available"]))
    return report


def create_argument_parser():
    argument_parser = argparse.ArgumentParser(description="This is magic script")
    argument_parser.add_argument("command", choices=["parse_har", "alarm", "parse_headers"])
    argument_parser.add_argument("path")
    argument_parser.add_argument("-v", "--verbose", action="store_true")
    return argument_parser


def create_logger(verbose):
    logger = logging.getLogger("barbora alarm")
    if verbose:
        logger.setLevel(level="DEBUG")
    else:
        logger.setLevel(LOG_LEVEL)
    ch = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger



if __name__ == "__main__":
    argument_parser = create_argument_parser()
    arguments = argument_parser.parse_args()
    logger = create_logger(arguments.verbose)
    path = arguments.path
    if arguments.command == "parse_har":
        har_path = path
        parse_har(har_path)
    elif arguments.command == "parse_headers":
        headers_path = path
        parse_headers(headers_path)
    elif arguments.command == "alarm":
        headers_path = path
        scrape_and_alarm(headers_path)
