# ⚠️ WARNING ⚠️

The [Python client library](https://github.com/influxdata/influxdb-python) that this project relies on has been retired. You should migrate to the [v2 version](https://github.com/loganmarchione/docker-speedtest-influxdbv2) of this container image.

Telegraf now has an official Internet Speed Monitor plugin. I recommend using that instead.

https://github.com/influxdata/telegraf/tree/master/plugins/inputs/internet_speed

# docker-speedtest-influxdb

Runs Ookla's [Speedtest CLI](https://www.speedtest.net/apps/cli) program in Docker, sends the results to InfluxDB
  - Source code: [GitHub](https://github.com/loganmarchione/docker-speedtest-influxdb)
  - Image base: [Python (slim Buster)](https://hub.docker.com/_/python)
  - Init system: N/A
  - Application: [Speedtest CLI](https://www.speedtest.net/apps/cli)
  - Architecture: `linux/amd64`

## Explanation

  - This runs Ooka's Speedtest CLI program on an interval, then writes the data to an InfluxDB database (you can later graph this data with Grafana or Chronograf)
  - This does **NOT** use the open-source [speedtest-cli](https://github.com/sivel/speedtest-cli). That program uses the Speedtest.net HTTP API. This program uses Ookla's official CLI application.
  - ⚠️ Ookla's speedtest application is closed-source (the binary applications are [here](https://www.speedtest.net/apps/cli)) and Ookla's reasoning for this decision is [here](https://www.reddit.com/r/HomeNetworking/comments/dpalqu/speedtestnet_just_launched_an_official_c_cli/f5tm9up/) ⚠️
  - ⚠️ Ookla's speedtest application reports all data back to Ookla ⚠️
  - ⚠️ This application uses Ookla's recommendation to install by piping curl to bash  ⚠️

## Requirements

  - This only works with InfluxDB 1.7 and lower, because I'm using [this](https://github.com/influxdata/influxdb-python) client library.
  - You must already have an InfluxDB database created, along with a user that has `WRITE` and `READ` permissions on that database.
  - This Docker container needs to be able to reach that InfluxDB instance by hostname, IP address, or Docker service name (I run this container on the same Docker network as my InfluxDB instance).
  - ⚠️ Depending on how often you run this, you may need to monitor your internet connection's usage. If you have a data cap, you could exceed it. The standard speedtest uses about 750MB of data per run. See below for an example. ⚠️

```
CONTAINER: NET I/O
speedtest: 225MB / 495MB
```

## Docker image information

### Environment variables
| Variable       | Required?                | Definition                       | Example                                     | Comments                                                                                         |
|----------------|--------------------------|----------------------------------|---------------------------------------------|--------------------------------------------------------------------------------------------------|
| INFLUXDB_HOST  | No (default: localhost)  | Server hosting the InfluxDB      | 'localhost' or your Docker service name     |                                                                                                  |
| INFLUXDB_PORT  | No (default: 8086)       | InfluxDB port                    | 8086                                        |                                                                                                  |
| INFLUXDB_USER  | Yes                      | Database username                | influx_username                             | Needs to have WRITE and READ permissions already                                                 |
| INFLUXDB_PASS  | Yes                      | Database password                | influx_password                             |                                                                                                  |
| INFLUXDB_DB    | Yes                      | Database name                    | SpeedtestStats                              | Must already be created, this does not create a DB                                               |
| SLEEPY_TIME    | No (default: 3600)       | Seconds to sleep between runs    | 3600                                        | The loop takes about 15-30 seconds to run, so I wouldn't set this value any lower than 60 (1min) |

### Ports
N/A

### Volumes
N/A

### Example usage

#### Build

```
git clone https://github.com/loganmarchione/docker-speedtest-influxdb.git
cd docker-speedtest-influxdb
sudo docker build --no-cache --file Dockerfile --tag loganmarchione/docker-speedtest-influxdb  .
```

#### Run

```
sudo docker run --name docker-speedtest-influxdb \
  --env INFLUXDB_HOST=influxdb \
  --env INFLUXDB_PORT=8086 \
  --env INFLUXDB_USER=influx_username \
  --env INFLUXDB_PASS=influx_password \
  --env INFLUXDB_DB=SpeedtestStats \
  --env SLEEPY_TIME=3600 \
  loganmarchione/docker-speedtest-influxdb
```

## TODO
- [ ] Learn Python
- [x] ~~Run the processes inside the container as a non-root user~~
- [ ] Add a [healthcheck](https://docs.docker.com/engine/reference/builder/#healthcheck)
- [ ] Move the database connection check to a function
- [ ] Add logic to check if variables are set
- [x] ~~Add defaults for HOST and PORT~~
- [ ] Update CI/CD with tests
- [x] ~~Add warning about bandwidth~~
