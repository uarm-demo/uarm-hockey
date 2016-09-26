"""
# This is a uArm hockey demo python script

# joystick is using Arduino, if you are interested on the Arduino source code. You could download it here.
#

# this script is base on pyuarm which is uArm Python Library. https://github.com/uArm-Developer/pyuarm
#
# (C) 2016 UFACTORY <developer@ufactory.cc>
"""
import pyuarm
from pyuarm.tools.list_uarms import get_uarm_port_cli, uarm_ports

import serial
import json, os, io, sys, time
import argparse

config_template = {
    "joystick_port": "",    # hockey port name
    "uarm_port": "",        # uArm port name
    "min_x": 0.0,           # minimum x value
    "max_x": 0.0,           # maximum x value
    "min_y": 0.0,           # minimum y value
    "max_y": 0.0,           # maximum y value
    "z": 0.0,               # stay z value
    "speed": 50,            # uArm move speed mm/sec
    "z_offset": "0",
    "min_z_offset": "150"   
}

"""
Getting Current working path and 'config.json'
"""
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)


def read_setting(config_filename):
    """
    Load Config from json file.
    config_filename default is 'config.json'
    """
    config_path = os.path.join(application_path, config_filename)
    if os.path.exists(config_path):
        with io.open(config_path, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
        return config
    else:
        print ("config.json not found, exit")
        sys.exit()


def write_setting(config,config_filename):
    """
    Save config to file, config is json file
    config_filename default is 'config.json'
    """
    config_path = os.path.join(application_path, config_filename)
    with io.open(config_path, "wb") as config_file:
        json.dump(config, config_file, ensure_ascii=False, sort_keys=True, indent=2, separators=(',', ': '))


def arduino_map(x, in_min, in_max, out_min, out_max):
    """
    copy the function map from Arduino
    """
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def get_joystick(uarm_port):
    """
    Choose hockey port, uarm_port is the port name which uArm take.
    """
    ports = []
    for p in uarm_ports():
        if p == uarm_port:  # if the port is used by uArm, remove it
            continue
        ports.append(p)
    if len(ports) > 1:
        i = 1
        for port in ports:
            print ("[{}] - {}".format(i, port))
            i += 1
        port_index = raw_input("Please Choose the JoyStick Port: ")  # input the number to choose the port
        uarm_port = ports[int(port_index) - 1]
        return uarm_port
    elif len(ports) == 1:
        return ports[0]
    elif len(ports) == 0:
        print ("No uArm ports is found.")
        return None


class Play:
    """
    Play Class, default config filename is config.json
    """
    x = 0.0
    y = 150.0
    z = 200.0

    def __init__(self,config_filename='config.json'):
        self.config = read_setting(config_filename)
        self.min_x = float(self.config['min_x'])
        self.max_x = float(self.config['max_x'])
        self.min_y = float(self.config['min_y'])
        self.max_y = float(self.config['max_y'])
        self.speed = float(self.config['speed'])
        # print (self.config)
        # print ("config: min_x".format(self.min_x))
        self.z = float(self.config['z'])
        self.uarm = pyuarm.UArm(port=self.config['uarm_port'])
        self.update_pos()
        self.joystick = serial.Serial(baudrate=115200, port=self.config['joystick_port'])
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
            # elif len(values) == 1:
            #     if values[0].lower() == "a":
            #         print ("Button A")
            #     elif values[0].lower() == "b":
            #         print ("Button B")
            #     elif values[0].lower() == "c":
            #         print ("Button C")
            #     elif values[0].lower() == "d":
            #         print ("Button D")
            #     elif values[0].lower() == "e":
            #         print ("Button E")
            #     elif values[0].lower() == "f":
            #         print ("Button F")

    def update_pos(self):
        """"
        Send the move command to uArm with current x,y
        """
        # if not self.uarm.is_moving():
        if self.y < float(self.config['min_z_offset']):  # this could fix the z value problem
            self.uarm.move_to(self.x,self.y,self.z - float(self.config['z_offset']), self.speed)
        else:
            self.uarm.move_to(self.x, self.y, self.z, self.speed)


class Setting:
    #default x,y,z position
    x = 0.0
    y = 150.0
    z = 200.0

    def __init__(self, config_filename='config.json'):
        """
        Setting Class
        :param config_filename:  default is "config.json"
        """
        self.config = config_template
        self.config_filename = config_filename
        print ("Reading Config File: {}".format(self.config))
        self.uarm = pyuarm.UArm(port=get_uarm_port_cli())
        self.joystick = serial.Serial(baudrate=115200, port=get_joystick(self.uarm.port))
        print ("connected to hockey: {}".format(self.joystick.port))
        print ("Saving port information to config file...")
        self.config['uarm_port'] = self.uarm.port
        self.config['joystick_port'] = self.joystick.port
        # self.save_config()
        self.update_pos()

    def save_config(self):
        """
        save config data to file
        """
        write_setting(self.config, self.config_filename)

    def reset(self):
        """
        reset uArm to center position but in the correct z position
        """
        self.x = 0.0
        self.y = 150.0
        if self.config['z'] > 0.0:
            self.z = float(self.config['z'])
        self.update_pos()

    def run(self):
        ################ Setting Z #####################
        print ("Setting Z...")  # Setting Z
        print ("C: z - 1, D: z + 1, E: Save Z ")
        while True:
            values = self.joystick.readline().strip().split("=")
            if len(values) == 1:
                if values[0].lower() == "c":
                    print ("Button C")
                    self.z -= 1
                    self.update_pos()
                    print ("z:" + str(self.z))
                elif values[0].lower() == "d":
                    print ("Button D")
                    self.z += 1
                    self.update_pos()
                    print ("z:" + str(self.z))
                elif values[0].lower() == "e":
                    print ("Button E")
                    print ("z:" + str(self.z))
                    self.config['z'] = str(self.z)
                    # self.save_config()
                    self.joystick.flushInput()
                    time.sleep(0.1)
                    break
            # if option.lower() == "x":
        ################ Setting X #####################
        min_x_done_flag = False
        max_x_done_flag = False
        print("Setting X...") # Setting X
        print ("C: x - 1, D: x + 1, F: Save maximum X, E: Save minimum X ")
        while True:
            if min_x_done_flag and max_x_done_flag:
                break
            values = self.joystick.readline().strip().split("=")
            if len(values) == 1:
                if values[0].lower() == "c":  # x -1
                    print ("Button C")
                    self.x -= 1
                    self.update_pos()
                    print ("x:" + str(self.x))
                elif values[0].lower() == "d":  # x + 1
                    print ("Button D")
                    self.x += 1
                    self.update_pos()
                    print ("x:" + str(self.x))
                elif values[0].lower() == "e":  # save minimum x
                    if not min_x_done_flag and self.x != 0.0:
                        print ("Button E")
                        print ("Minimum x:" + str(self.x))
                        self.config['min_x'] = str(self.x)
                        min_x_done_flag = True
                elif values[0].lower() == "f":  # save maximum x
                    if not max_x_done_flag and self.x != 0.0:
                        print ("Button F")
                        print ("Maximum x:" + str(self.x))
                        self.config['max_x'] = str(self.x)
                        max_x_done_flag = True
        # self.save_config()
        self.reset()
        ################ Setting Y #####################
        min_y_done_flag = False
        max_y_done_flag = False
        print("Setting Y...")
        print ("C: y - 1, D: y + 1, F: Save maximum Y, E: Save minimum Y ")
        while True:
            if min_y_done_flag and max_y_done_flag:
                break
            values = self.joystick.readline().strip().split("=")
            if len(values) == 1:
                if values[0].lower() == "c":  # y -1
                    print ("Button C")
                    self.y -= 1
                    self.update_pos()
                    print ("y:" + str(self.x))
                elif values[0].lower() == "d":  # y + 1
                    print ("Button D")
                    self.y += 1
                    self.update_pos()
                    print ("y:" + str(self.y))
                elif values[0].lower() == "e":  # save minimum y
                    if not min_y_done_flag and self.y != 150.0:
                        print ("Button E")
                        print ("Minimum y:" + str(self.y))
                        self.config['min_y'] = str(self.y)
                        min_y_done_flag = True
                elif values[0].lower() == "f":  # save maximum y
                    if not max_y_done_flag and self.y != 150.0:
                        print ("Button F")
                        print ("Maximum y:" + str(self.y))
                        self.config['max_y'] = str(self.y)
                        max_y_done_flag = True
        self.save_config()
        self.reset()

    def update_pos(self):
        self.uarm.move_to(self.x, self.y, self.z, 50)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Enter the Config mode", action="store_true")
    parser.add_argument("-f", "--file", nargs='?', help="provide the config file path")
    args = parser.parse_args()
    config_file = None
    if args.file:
        config_file = args.file
    if args.config:
        setting = Setting(config_file)
        setting.run()
        sys.exit()
    play = Play(config_file)
    play.run()

if __name__ == '__main__':
    main()