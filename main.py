#!/usr/bin/env python3

import base64
import configparser
from datetime import datetime
import json

import paho.mqtt.client as mqtt

from groups import group1, group2, group3, group4, group5, group6, group7, group8
from groups import group9, group10, group11

# Read in config file with MQTT details.
config = configparser.ConfigParser()
config.read("ttn-mqtt\config.ini")

# MQTT broker details
broker_address = config["mqtt"]["broker"]
username = config["mqtt"]["username"]
password = config["mqtt"]["password"]

# MQTT topic to subscribe to. We subscribe to all uplink messages from the
# devices.
u_topic = "v3/+/devices/+/up"
d_topic = "v3/+/devices/+/down/push"  #subsribing to downlink
receive_count=0
send_count=0 #counters for prr
decoders = {
    1: group1.decode,
    2: group2.decode,
    3: group3.decode,
    4: group4.decode,
    5: group5.decode,
    6: group6.decode,
    7: group7.decode,
    8: group8.decode,
    9: group9.decode,
    10: group10.decode,
    11: group11.decode,
}

# Callback when successfully connected to MQTT broker.
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker.")

    if rc != 0:
        print(" Error, result code: {}".format(rc))

def prr():
    if send_count>0:
        prr=(receive_count/send_count)*100
        prrf=round(prr,2)
        print("\nPacket Reception Rate = ",prrf)
        o_p="D:/Downloads/IOT Final Project/result.txt"
        with open(o_p, 'a') as f:
            #f.write(prrf + '\n')
            f.write(f"{prrf}\n") 
    else:
        print("No uplink packets transmitted yet, PRR calculation cannot be performed.") 
# Callback function to handle incoming MQTT messages
def on_message(client, userdata, message):
    global receive_count, send_count
    # Timestamp on reception.
    current_date = datetime.now()

    # Handle TTN packet format.
    message_str = message.payload.decode("utf-8")
    message_json = json.loads(message_str)
    if message.topic.endswith("/up"):  # checking whether it is uplink 
        encoded_payload = message_json["uplink_message"]["frm_payload"]
        raw_payload = base64.b64decode(encoded_payload)

        if len(raw_payload) == 0:
            return
        # Nothing we can do with an empty payload.
          

    # First byte should be the group number, remaining payload must be parsed.
        group_number = raw_payload[0]
        remaining_payload = raw_payload[1:]

    # See if we can decode this payload.
        if group_number in decoders:
            try:
                temperature = decoders[group_number](remaining_payload)
            except:
                print("Failed to decode payload for Group {}".format(group_number))
                #print("  payload: {}".format(remaining_payload))
                return

            if temperature == None:
                print("Undecoded message from Group {}".format(group_number))
            else:
                #res = "{} temperature: {}".format(current_date.isoformat(), temperature)
                send_count = send_count+1
                print("\nUplink Count = ",send_count)
                # o_p="D:/Downloads/IOT Final Project/result.txt"
                # with open(o_p,'a') as f:
                #     f.write(send_count+'\n')
        # modified to print the results and store it in a txt file
            #print("{} temperature: {}".format(current_date.isoformat(), temperature))
        else:
            print("Received message with unknown group: {}".format(group_number))

    elif message.topic.endswith("/down/push"):# checking whether it is downlink
    # else: 
    #     receive_count=receive_count+1
    #     print("\n Downlink Count = ",receive_count)
    #     prr()   #debugging step after debug remove above 3 lines and uncomment below
        if "downlink_message" in message_json:
            downlink_message= message_json["downlink_message"]
            dev_eui=message_json["end_device_ids"]["device_id"]
            downlink_paylod=downlink_message.get("frm_payload","")
            
            if downlink_paylod:
                 decoded_payload = base64.b64decode(downlink_paylod)
                 rssi = None
                 snr = None
                 datarate = None 
                # Extract RSSI, SNR, and datarate info
                 if "rx_metadata" in downlink_message:
                     for metadata in downlink_message["rx_metadata"]:
                         rssi = metadata.get("rssi", None)
                         snr = metadata.get("snr", None)
                         # You can infer the datarate from tx_info or rx_metadata
                         # Typically, the datarate is found under the tx_info or the metadata structure.
                         # Adjust this part based on your exact needs.
                         if "tx_info" in downlink_message:
                             datarate = downlink_message["tx_info"].get("datarate", None)             
                           # Print or process the downlink payload and metrics
                 #res = f"{current_date.isoformat()} - Downlink message for device {dev_eui}: {decoded_payload}, RSSI: {rssi}, SNR: {snr}, Datarate: {datarate}"
                 receive_count=receive_count+1
                 print("\n Downlink Count = ",receive_count)

                #Optionally, save the downlink message data to a file.
                 #o_p = "D:/Downloads/IOT Final Project/result.txt"
                 #with open(o_p, 'a') as f:
                  #   f.write(receive_count + '\n')
                 prr() #calling ppr function bug
            else:
                print("No payload in downlink message.")
        else:
            print("Received message that is not a downlink message.")
# MQTT client setup
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

# Setup callbacks.
client.on_connect = on_connect
client.on_message = on_message

# Connect to broker.
client.username_pw_set(username, password)
client.tls_set()
client.connect(broker_address, 8883)

# Subscribe to the MQTT topic and start the MQTT client loop
client.subscribe(u_topic)
client.subscribe(d_topic)
client.loop_forever()
