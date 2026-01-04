# -*- coding: utf-8 -*-
"""
Created on Mon Dec 15 09:32:41 2025

@author: User
"""

from serial.tools import list_ports

ports = list_ports.comports()

for p in ports:
    print({
        "device": p.device,          # COM3
        "name": p.name,              # COM3
        "description": p.description,# USB-SERIAL CH340
        "hwid": p.hwid,              # VID:PID=1A86:7523
        "vid": p.vid,                # Vendor ID (int or None)
        "pid": p.pid,                # Product ID (int or None)
        "serial_number": p.serial_number,
        "location": p.location,
        "manufacturer": p.manufacturer
    })

from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient(
    port="COM4",
    baudrate=19200,
    bytesize=8,
    parity="E",
    stopbits=1,
    timeout=1
)


if not client.connect():
    raise RuntimeError("Failed to open COM3")
