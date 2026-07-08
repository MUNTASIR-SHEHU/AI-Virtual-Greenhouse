import json
import time
import os

def get_latest_log_entry():
    try:
        with open('system_log.json', 'r') as f:
            data = json.load(f)
            return data[-1]
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

def print_dashboard():
    latest_entry = get_latest_log_entry()
    if latest_entry is None:
        print("No log entries found.")
        return

    temperature = latest_entry['temperature']
    moisture = latest_entry['moisture']
    heater_on = latest_entry['heater_on']
    pump_on = latest_entry['pump_on']

    print("Temperature: {:.2f}°C".format(temperature))
    print("Moisture: {:.2f}%".format(moisture))
    print("Heater: {}".format("ON" if heater_on else "OFF"))
    print("Pump: {}".format("ON" if pump_on else "OFF"))

while True:
    os.system('clear')
    print_dashboard()
    time.sleep(0.5)