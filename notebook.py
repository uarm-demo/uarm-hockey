import pyuarm
from pyuarm.tools.list_uarms import get_uarm_port_cli, uarm_ports

import serial
from serial.tools.list_ports import comports
import json, os, io, sys, time
import logging

def get_port_from_serial_id(serial_id):
    ports = comports()
    for p in ports:
        if p.serial_number == serial_id:
            return p[0]


def get_serial_id_from_port_name(port_name):
    ports = comports()
    for p in ports:
        if p.name == port_name:
            return p.serial_number

def arduino_map(x, in_min, in_max, out_min, out_max):
    """
    copy the function map from Arduino
    """
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

class Play:
    """
    Play Class, default config filename is config.json
    """
    x = 0.0
    y = 150.0
    z = 200.0

    def __init__(self,config):
        self.config = config
        # logging.basicConfig(filename=self.config["log_filename"], level=print)
        self.min_x = float(self.config['min_x'])
        self.max_x = float(self.config['max_x'])
        self.min_y = float(self.config['min_y'])
        self.max_y = float(self.config['max_y'])
        self.speed = float(self.config['speed'])
        # print (self.config)
        # print ("config: min_x".format(self.min_x))
        self.z = float(self.config['z'])
        self.uarm = pyuarm.UArm(port=get_port_from_serial_id(self.config['uarm_serial_port_id']))
        self.update_pos()
        self.joystick = serial.Serial(baudrate=115200, port=get_port_from_serial_id(self.config['joystick_serial_port_id']))
        print ("connected to hockey: {}".format(self.joystick.port))

    def run(self):

        while True:
            values = self.joystick.readline().strip().split("=")  # read line from hockey like 'x = 123'
            if len(values) > 1:
                if values[0].lower() == "x":
                    self.x = arduino_map(float(values[1]), -520, 470, self.min_x, self.max_x)  # mapping x
                    print ("X: {}".format(self.x))
                    self.update_pos()

                elif values[0].lower() == "y":
                    self.y = arduino_map(float(values[1]), -520, 470, self.min_y, self.max_y)  # mapping y
                    print ("Y: {}".format(self.y))
                    self.update_pos()

    def update_pos(self):
        """"
        Send the move command to uArm with current x,y
        """
        # if not self.uarm.is_moving():
        if self.y < float(self.config['min_z_offset']):  # this could fix the z value problem
            self.uarm.move_to(self.x,self.y,self.z - float(self.config['z_offset']), self.speed)
        else:
            self.uarm.move_to(self.x, self.y, self.z, self.speed)


config1 = {
  "joystick_serial_port_id": "A6031WJ9",
  "max_x": "56.0",
  "max_y": "250.0",
  "min_x": "-127.0",
  "min_y": "132.0",
  "speed": "50",
  "uarm_serial_port_id": "AI041AEM",
  "z": "115.0",
  "z_offset" : "10",
  "min_z_offset": "150",
  "log_filename": "/home/pi/hockey/log_1.log"
}

config2 = {
  "joystick_serial_port_id": "A6031WRN",
  "max_x": "79.0",
  "max_y": "280.0",
  "min_x": "-121.0",
  "min_y": "155.0",
  "speed": "50",
  "uarm_serial_port_id": "AL01H3QZ",
  "z": "102.0",
  "z_offset" : "0",
  "min_z_offset": "150",
  "log_filename": "/home/pi/hockey/log_2.log"
}

play1 = Play(config1)
# play2 = Play(config2)
play1.run()
# play2.run()            