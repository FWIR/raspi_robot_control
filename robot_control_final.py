#!/usr/bin/python

import RPi.GPIO as GPIO
from datetime import datetime
from time import sleep
import os
import requests
import json
import math
import time



###########################################################
#API Robot Stuff
###########################################################

base_url = 'https://api.interactions.ics.unisg.ch/cherrybot'
#base_url = 'https://api.interactions.ics.unisg.ch/pretendabot'

# login put request
def login():
    print("login")
    login_data = { "name": "Florian", "email": "florian.wirth@unisg.ch"}
    print(login_data)
    response = requests.post(base_url + "/operator", json = login_data)
    print(response.status_code)
    time.sleep(2)
    return response.status_code

# get request for user information     
def get_user():
    print("get_user")
    response = requests.get(base_url + "/operator", {})
    print(response.status_code)
    time.sleep(1)
    return response.json()

# put request to move robot to default position
def init_robot(token):
    print("init robot")
    headers = {"Authentication": token }
    response = requests.put(base_url + "/initialize", headers= headers)
    print(response.status_code)
    time.sleep(2)
    return response.status_code

# get request to obtain current TCP of robot
def get_current_position(token):
    print("get current position")
    headers = {"Authentication": token }
    response = requests.get(base_url + "/tcp", headers= headers)
    print(response.status_code)
    print("current position:")
    print(response.json())
    time.sleep(2)
    return response.json()

# put request to push the new target position
def move_robot(tar_pos, token):
    print("put target position")
    headers = { "Authentication": token }
    data = { "target": tar_pos, "speed": 200}
    response = requests.put(base_url + "/tcp/target", json=data, headers=headers,)
    print(data)
    print(response.status_code)
    time.sleep(2)
    return response.status_code

# put request to move change gripper
def change_gripper(token, gripper):
    print("change gripper")
    if gripper == 0:
        gripper = 100
    else:
        gripper = 0

    headers = {"Authentication": token }
    response = requests.put(base_url + "/gripper", headers= headers, json=gripper)
    print(response.status_code)
    time.sleep(2)
    return gripper

# delete request to logout with token
def logout(token):
    print("logging out")
    requests.delete(base_url + "/operator/" + token)



###########################################################
#target location calculation
###########################################################

# handle command and call corresponding target calculation function
def set_target(command, current_position):
    if command == "move_clockwise":
        target = move_clockwise(current_position)
    elif command == "move_counterclockwise":
        target = move_counterclockwise(current_position)
    elif command == "move_forward":
        target = move_forward(current_position)
    elif command == "move_backward":
        target = move_backward(current_position)
    return target

# handle special angles else calculate radiant normally
def get_radiant(x,y):
    if x == 0 and y > 0:
        radiant = math.radians(90)
    elif x == 0 and y < 0:
        radiant = math.radians(-90)
    elif y == 0 and x > 0:
        radiant = math.radians(0)
    elif y == 0 and x < 0: 
        radiant = math.radians(180)
    else:
        radiant = math.atan2(y,x)
    return radiant

# calculate target for moving forward
def move_forward(cur_pos):
    print("move_forward")
    # get cur_pos and set tar_pos with startin values
    tar_pos = cur_pos
    x = cur_pos.get("coordinate").get("x")
    y = cur_pos.get("coordinate").get("y")

    # get radiant
    radiant = get_radiant(x,y)

    # setting new coordinate and handle if pointing to positive or negative coordinate
    if x > 0:
        x = x + 100 * abs(math.cos(radiant))
    else:
        x = x - 100 * abs(math.cos(radiant))
    if y > 0:
        y= y + 100 * abs(math.sin(radiant))
    else:
        y= y - 100 * abs(math.sin(radiant))
    
    # update tar_pos 
    tar_pos["coordinate"]["x"] = x
    tar_pos["coordinate"]["y"] = y
    
    return tar_pos
    
# calculate target for moving backward
def move_backward(cur_pos):
    print("move_backward")
    # get cur_pos and set tar_pos with starting values
    tar_pos = cur_pos
    x = cur_pos.get("coordinate").get("x")
    y = cur_pos.get("coordinate").get("y")

    # get radiant
    radiant = get_radiant(x,y)

    # setting new coordinate and handle if pointing to positive or negative coordinate
    if x > 0:
        x = x - 100 * abs(math.cos(radiant))
    else:
        x = x + 100 * abs(math.cos(radiant))
    if y > 0:
        y= y - 100 * abs(math.sin(radiant))
    else:
        y= y + 100 * abs(math.sin(radiant))
    
    # update tar_pos 
    tar_pos["coordinate"]["x"] = x
    tar_pos["coordinate"]["y"] = y
    
    return tar_pos

# calculate target for moving clockwise
def move_clockwise(cur_pos):
    print("move_clockwise")
    # get cur_pos and set tar_pos with startin values
    tar_pos = cur_pos
    x = cur_pos.get("coordinate").get("x")
    y = cur_pos.get("coordinate").get("y")
    yaw = cur_pos.get("rotation").get("yaw")

    # get radiant
    radiant = get_radiant(x,y)

    #setting new coordinates
    x = math.sqrt((x*x + y*y)) * math.cos(radiant - math.radians(12))
    y = math.sqrt((x*x + y*y)) * math.sin(radiant - math.radians(12))
    yaw = yaw - 12

    # update tar_pos 
    tar_pos["coordinate"]["x"] = x
    tar_pos["coordinate"]["y"] = y
    tar_pos["rotation"]["yaw"] = yaw
    
    return tar_pos

# calculate target for moving counterclockwise
def move_counterclockwise(cur_pos):
    print("move_counterclockwise")
    # get cur_pos and set tar_pos with startin values
    tar_pos = cur_pos
    x = cur_pos.get("coordinate").get("x")
    y = cur_pos.get("coordinate").get("y")
    yaw = cur_pos.get("rotation").get("yaw")

    # get radiant
    radiant = get_radiant(x,y)

    #setting new coordinates
    x = math.sqrt((x*x + y*y)) * math.cos(radiant + math.radians(12))
    y = math.sqrt((x*x + y*y)) * math.sin(radiant + math.radians(12))
    yaw = yaw + 12

    # update tar_pos 
    tar_pos["coordinate"]["x"] = x
    tar_pos["coordinate"]["y"] = y
    tar_pos["rotation"]["yaw"] = yaw
    
    return tar_pos


###################################################
# Main Code
###################################################


############
# getting robot ready#
############

print("start execution")

# login
status = login()

# exit if login failed
if status !=200:
   exit()

# get user info
user = get_user()

# save access token
print("saving token")
token = user.get("token")

# initalize robot to starting posiont
init_robot(token)

# set-up gripper that it is closed
gripper = 100
gripper = change_gripper(token, gripper)


############
# CONSTANTS#
############
# Input pin is 3 (GPIO2)
INPUT_PIN = 3
# To turn on debug print outs, set to 1
DEBUG = 1

###################
# INITIALIZE PINS #
###################
GPIO.setmode(GPIO.BOARD)
GPIO.setup(INPUT_PIN, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(INPUT_PIN, GPIO.IN)

# Main loop, listen for infinite packets
while True:
    print("\nWaiting for GPIO")

    # If there was a transmission, wait until it finishes
    #GPIO.wait_for_edge(INPUT_PIN, GPIO.RISING)
    value = 1
    while value:
        sleep(0.001)
        #print("Last read value: {}".format(value))
        value = GPIO.input(INPUT_PIN)       

    # timestamps for pulses and packet reception
    startTimePulse = datetime.now()
    previousPacketTime = 0

    print("\nListening for an IR packet")

    # Buffers the pulse value and time durations
    pulseValues = []
    timeValues = []

    # decoded value initialization
    decoded_value = ""
    

    # Variable used to keep track of state transitions
    previousVal = 0

    # Inner loop 
    while True:
        # Measure time up state change
        if value != previousVal:
            # The value has changed, so calculate the length of this run
            now = datetime.now()
            pulseLength = now - startTimePulse
            startTimePulse = now

            # Record value and duration of current state
            pulseValues.append(value)
            timeValues.append(pulseLength.microseconds)
            
            # Detect short IR packet using packet length and special timing
            if(len(pulseValues) == 3):
                if(timeValues[1] < 3000):
                    print("Detected Short IR packet")
                    print(pulseValues)
                    print(timeValues)
                    break;

            # Detect standard IR packet using packet length 
            if(len(pulseValues) == 67):
                if(DEBUG==1):
                    print("Finished receiving standard IR packet")
                    print(pulseValues)
                    print(timeValues)
                    
                    # read out the timing values to decode signal
                    for x in range(3,66,2): 
                        if timeValues[x] > 1000:
                            decoded_value = decoded_value + "1"
                        else:
                            decoded_value = decoded_value + "0"

                    print(decoded_value) 
                 

                    #assign decoded value to command
                    if decoded_value == "00000000111111110001100011100111":
                        command = "move_forward"
                    elif decoded_value == "00000000111111110100101010110101":
                        command = "move_backward"
                    elif decoded_value == "00000000111111110001000011101111":
                        command = "move_counterclockwise"
                    elif decoded_value == "00000000111111110101101010100101":
                        command = "move_clockwise"
                    elif decoded_value == "00000000111111110011100011000111":
                        command = "gripper"
                    elif decoded_value == "00000000111111111011000001001111":
                        command = "logout"
                    else:
                        command = "not_found"

                    print(command)

                    # logout and exit programm if command == logout
                    if command == "logout":
                        logout(token)
                        exit()

                    # if commad is gripper, change gripper
                    elif command == "gripper":
                        gripper = change_gripper(token, gripper)

                    # handle command not found
                    elif command == "not_found":
                        print("command not found")

                    # move robot to new target position
                    else:
                        # get current position
                        current_position = get_current_position(token)

                        # calculate target based on command
                        target = set_target(command, current_position)

                        # send target to robot to make it move
                        move_robot(target, token)

                    
                    break;

        # save state
        previousVal = value
        # read GPIO pin
        value = GPIO.input(INPUT_PIN)
