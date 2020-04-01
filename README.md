# barbora-delivery-spot-alert

Tool that signals when delivery spot opens

This repository is for educational purposes only.

As a reaction to COVID-19 pandemic a lot of Lithuanian would like to shop online.

Unfortunately most popular online supermarket BARBORA.lt is not able to address rising demand.

This repository contains an example script that could help you to get signal when there are open delivery timeslots.


## Instalation

Requires Python > 3

```sh
pip install -r requirements.txt
```

## Usage

### Get Headers
1. Visit www.barbora.lt
2. Enter devtools (F12)
3. Choose Network tag
4. Choose a delivery address/pickup in website
5. (absolete) Check devtools, right click on any line and select "Save all as HAR"
5. Check devtools, right click request title "deliveries" select "Save request Headers"
6. Put headers to file (for example "header") in the same directory as main.py

### Extract Headers from headers file

Extract headers from har file by running:
```sh
python main.py parse_headers "headers.txt"
```

This will create `"path to har headers.txt.json"` with all required headers


Then, run the monitoring system
```sh
python main.py alarm headers.txt.json"
```

Everytime script finds a slot it text or beep.


## Web app

- There is a flask web app at ./app.py
- To run dev server "python app.py"
- App will hit API every 60 seconds and send Server-Sent event (https://www.w3schools.com/html/html5_serversentevents.asp)
- It will play a sounds every time an open slot is found


## Version tracked

- Flask Web app
- Linux ALSA support
- MacOs support
- Header extraction from Request headers.
- Header extraction from HAR

## OS support
- Windows Beep sound
- Linux @robertasmurnikovas and @montvid
- MacOs @sidlauskaslukas
