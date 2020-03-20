# barbora-delivery-spot-alert

Tool that signals when delivery spot opens

This repository is for educational purposes only.

As a reaction to COVID-19 pandemic a lot of Lithuanian would like to shop online.

Unfortunately most popular online supermarket BARBORA.lt is not able to address rising demand.

This repository contains an example script that could help you to get signal when there are open delivery timeslots.

## Usage

### Get HAR

1. Visit www.barbora.lt
2. Enter devtools (F12)
3. Choose Network tag
4. Choose a delivery address/pickup in website
5. Check devtools, right click on any line and select "Save all as HAR"
6. Put HAR file in the same directory as main.py

### Extract Headers from HAR


Extract har file
```sh
python main.py parse_har "path to HAR file.har"
```

This will create `"path to har file.har.json"` with all required headers


Then, run the monitoring system
```sh
python main.py alarm "path to har file.har.json"
```

Everytime script finds a slot it will beep.
