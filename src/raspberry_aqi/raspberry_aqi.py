#! coding: utf-8
from __future__ import unicode_literals, print_function, division
import sys
from influxdb import InfluxDBClient
import pms7003


def read_config():
    with open(sys.argv[1]) as f:
        lines = f.readlines()
    config = {}
    for line in lines:
        if line.strip():
            k, v = line.strip().split('=')
            config[k] = v
    return config

if __name__ == '__main__':
    data = None
    retries = 1
    while True:
        if retries >= 3:
            exit(-1)
        data = pms7003.read_data()
        if not data:
            retries += 1
            continue
        if data['errcode'] != '\0':
            retries += 1
            continue
        break
    config = read_config()
    json_data = {
        "measurement": config['measurement'],
        "tags": {
            "location": config['location'],
            "device": config['device'],
            "version": data['version'],
            "city": config['city']
        },
        "fields": {
            "pm1.0@cf1": data['data'][pms7003.P_CF_PM10][1],
            "pm2.5@cf1": data['data'][pms7003.P_CF_PM25][1],
            "pm10@cf1": data['data'][pms7003.P_CF_PM100][1],
            "pm1.0": data['data'][pms7003.P_C_PM10][1],
            "pm2.5": data['data'][pms7003.P_C_PM25][1],
            "pm10": data['data'][pms7003.P_C_PM100][1],
            "dl0.3@0.1l": data['data'][pms7003.P_C_03][1],
            "dl0.5@0.1l": data['data'][pms7003.P_C_05][1],
            "dl1.0@0.1l": data['data'][pms7003.P_C_10][1],
            "dl2.5@0.1l": data['data'][pms7003.P_C_25][1],
            "dl5.0@0.1l": data['data'][pms7003.P_C_50][1],
            "dl10@0.1l": data['data'][pms7003.P_C_100][1],
        }
    }
    client = InfluxDBClient(database=config['database'])
    client.write(json_data)
