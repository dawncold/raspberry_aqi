#! coding: utf-8
from __future__ import unicode_literals, print_function, division
import serial

SERIAL_DEVICE = '/dev/ttyAMA0'
HEAD_FIRST = 0x42
HEAD_SECOND = 0x4d
DATA_LENGTH = 32
BODY_LENGTH = DATA_LENGTH - 1 - 1
P_CF_PM10 = 2
P_CF_PM25 = 4
P_CF_PM100 = 6
P_C_PM10 = 8
P_C_PM25 = 10
P_C_PM100 = 12
P_C_03 = 14
P_C_05 = 16
P_C_10 = 18
P_C_25 = 20
P_C_50 = 22
P_C_100 = 24
DATA_DESC = [
    (P_CF_PM10, 'CF=1, PM1.0', 'μg/m3'),
    (P_CF_PM25, 'CF=1, PM2.5', 'μg/m3'),
    (P_CF_PM100, 'CF=1, PM10', 'μg/m3'),
    (P_C_PM10, 'PM1.0', 'μg/m3'),
    (P_C_PM25, 'PM2.5', 'μg/m3'),
    (P_C_PM100, 'PM10', 'μg/m3'),
    (P_C_03, '0.1L, d>0.3μm', ''),
    (P_C_05, '0.1L, d>0.5μm', ''),
    (P_C_10, '0.1L, d>1μm', ''),
    (P_C_25, '0.1L, d>2.5μm', ''),
    (P_C_50, '0.1L, d>5.0μm', ''),
    (P_C_100, '0.1L, d>10μm', ''),
]


def get_frame(_serial):
    while True:
        b = _serial.read()
        if b != chr(HEAD_FIRST):
            continue
        b = _serial.read()
        if b != chr(HEAD_SECOND):
            continue
        body = _serial.read(BODY_LENGTH)
        if len(body) != BODY_LENGTH:
            continue
        return body


def get_frame_length(_frame):
    h8 = ord(_frame[0])
    l8 = ord(_frame[1])
    return int(h8 << 8 | l8)


def get_version_and_error_code(_frame):
    return _frame[-4], _frame[-3]


def valid_frame_checksum(_frame):
    checksum = ord(_frame[-2]) << 8 | ord(_frame[-1])
    calculated_checksum = HEAD_FIRST + HEAD_SECOND
    for field in _frame[:-2]:
        calculated_checksum += ord(field)
    return checksum == calculated_checksum


def decode_frame(_frame):
    data = {}
    for item in DATA_DESC:
        start, desc, unit = item
        value = int(ord(_frame[start]) << 8 | ord(_frame[start + 1]))
        data[start] = value
    return data


def read_data():
    ser = serial.Serial(port=SERIAL_DEVICE, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE)
    try:
        frame = get_frame(ser)
    except Exception as e:
        print('get frame got exception: {}'.format(e.message))
    else:
        if not valid_frame_checksum(frame):
            print('frame checksum mismatch')
            return
        data = {'data': decode_frame(frame)}
        version, error_code = get_version_and_error_code(frame)
        data['version'] = version
        data['errcode'] = error_code
        return data
    finally:
        ser.close()


if __name__ == '__main__':
    data = read_data()
    if not data:
        print('no data')
        exit(0)
    if data['errcode'] != '\0':
        print('got error: {}'.format(data['errcode']))
        exit(-1)
    for k in sorted(data['data'], key=lambda x: int(x)):
        v = data['data'][k]
        print('{}: {} {}'.format(v[0], v[1], v[2]))
