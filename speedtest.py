#!/usr/bin/env python3

import datetime
import json
import os
import subprocess
import time
import sys
from influxdb import InfluxDBClient
import influxdb.exceptions

# Variables
influxdb_host = os.getenv("INFLUXDB_HOST", "localhost")
influxdb_port = int(os.getenv("INFLUXDB_PORT", 8086))
influxdb_user = os.getenv("INFLUXDB_USER")
influxdb_pass = os.getenv("INFLUXDB_PASS")
influxdb_db = os.getenv("INFLUXDB_DB")
sleepy_time = int(os.getenv("SLEEPY_TIME", 3600))
start_time = datetime.datetime.utcnow().isoformat()

# Some logging
print("#####\nScript starting!\n#####")
print("STATE: Starting at", start_time)
print("STATE: Sleep time between runs set to", sleepy_time, "seconds")


def loop():
    current_time = datetime.datetime.utcnow().isoformat()
    print("STATE: Loop running at", current_time)

    # Run Speedtest
    print("STATE: Speedtest running")
    my_speed = subprocess.run(['/usr/bin/speedtest', '--accept-license', '--accept-gdpr', '--format=json'], stdout=subprocess.PIPE, text=True, check=True)

    # Convert the string into JSON, only getting the stdout and stripping the first/last characters
    my_json = json.loads(my_speed.stdout.strip())

    # Get the values from JSON and log them to the Docker logs
    speed_down = my_json["download"]["bandwidth"]
    speed_up = my_json["upload"]["bandwidth"]
    ping_latency = my_json["ping"]["latency"]
    ping_jitter = my_json["ping"]["jitter"]
    timestamp = my_json["timestamp"]
    result_url = my_json["result"]["url"]

    print("STATE: Your download is", speed_down, "bps")
    print("STATE: Your upload is", speed_up, "bps")
    print("STATE: Your ping latency is", ping_latency, "ms")
    print("STATE: Your ping jitter is", ping_jitter, "ms")
    print("STATE: Your URL is", result_url, " --- This is not saved to InfluxDB")

    # Create a JSON file to send to InfluxDB
    json_body = [
        {
            "measurement": "speedtest",
            "tags": {
                "service": "speedtest"
            },
            "time": timestamp,
            "fields": {
                "download": speed_down,
                "upload": speed_up,
                "ping_latency": ping_latency,
                "ping_jitter": ping_jitter
            }
        }
    ]

    # Instantiate the connection
    print("STATE: Connecting to InfluxDB...")
    client = InfluxDBClient(host=influxdb_host, port=influxdb_port, username=influxdb_user, password=influxdb_pass, database=influxdb_db, timeout=15)

    # Try to connect
    try:
        result = client.ping()
        print("STATE: Connected to InfluxDB successfully - version is", result)
        print("STATE: Writing to database")
        client.write_points(json_body)
    except influxdb.exceptions.InfluxDBClientError as err:
        print("ERROR: Error with client")
        print(err)
        sys.exit(1)
    except influxdb.exceptions.InfluxDBServerError as err:
        print("ERROR: Error with server")
        print(err)
        sys.exit(1)
    except Exception as err:
        print(err)

    print("STATE: Sleeping for", sleepy_time, "seconds")
    time.sleep(sleepy_time)


while True:
    loop()
