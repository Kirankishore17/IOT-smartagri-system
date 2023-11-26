import time
import sys
from Adafruit_IO import MQTTClient
import paho.mqtt.client as paho

# Adafruit IO Feed/Topic 
ADAFRUIT_LED1_FEED = "led1"
ADAFRUIT_LED2_FEED = "led2"
ADAFRUIT_BUZZER_FEED = "buzzer"
ADAFRUIT_TEMPERATURE_FEED = "temperature"
ADAFRUIT_HUMIDITY_FEED = "humidity"
ADAFRUIT_FIRE_FEED = "fire"

# Gateway Info
CLIENT_ADDRESS = "192.168.1.215"
#CLIENT_ADDRESS = "192.168.2.42"
CLIENT_PORT = 1883

# MQTT Client Topic
CLIENT_TOPIC_LED1 = "led1temp"
CLIENT_TOPIC_LED2 = "led2hum"
CLIENT_TOPIC_HUMIDITY = "sensorhum"
CLIENT_TOPIC_TEMPERATURE = "sensortemp"
CLIENT_TOPIC_BUZZER = "buzz"
CLIENT_TOPIC_FLAME = "sensorflame"

# Internal status of sensors and actuators 
gateway_status = True
STATUS_OFF ="OFF"
STATUS_ON = "ON"
STATUS_HIGH ="HIGH"
STATUS_LOW ="LOW"

# Local variables
TEMP_UPPERLIMIT = 30
TEMP_LOWERLIMIT = 20
HUMIDITY_UPPERLIMIT = 30
HUMIDITY_LOWERLIMIT = 15

# Adafruit IO username and key
ADAFRUIT_IO_USERNAME = 'kirankishorekk'
ADAFRUIT_IO_KEY = 'aio_mTzd371eQTGSNAR41Yn8gauOBdLN'

ADAFRUIT_SUBSCRIBED_FEED = [ADAFRUIT_LED1_FEED, ADAFRUIT_LED2_FEED, ADAFRUIT_BUZZER_FEED]
ADAFRUIT_PUBLISH_FEED = [ADAFRUIT_TEMPERATURE_FEED, ADAFRUIT_HUMIDITY_FEED, ADAFRUIT_FIRE_FEED]

CLIENT_SUBSCRIBED_FEED = [CLIENT_TOPIC_HUMIDITY, CLIENT_TOPIC_TEMPERATURE, CLIENT_TOPIC_FLAME]
CLIENT_PUBLISH_FEED = [CLIENT_TOPIC_LED1, CLIENT_TOPIC_LED2, CLIENT_TOPIC_BUZZER]

adafruit_client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
paho_client = paho.Client("gateway")

# Function will be called when Client is disconnected    
def on_disconnect(client, userdata, message):
    print('Disconnected Successfully!!')

# Function will be called when a subscribed topic has a new value from client
# the message parameter has the feed/topic and new value published 
def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    print('--> Topic \'{0}\' received new value from Client: {1}'.format(message.topic, msg))
    # Operate the LED based on Temperature and Humidity level
    if message.topic == CLIENT_TOPIC_TEMPERATURE:
        adafruit_client.publish(ADAFRUIT_TEMPERATURE_FEED, msg)
        if float(msg) > TEMP_UPPERLIMIT or float(msg) < TEMP_LOWERLIMIT:
            paho_client.publish(CLIENT_TOPIC_LED1, STATUS_ON)
            adafruit_client.publish(ADAFRUIT_LED1_FEED, STATUS_ON)
    if message.topic == CLIENT_TOPIC_HUMIDITY:
        adafruit_client.publish(ADAFRUIT_HUMIDITY_FEED, msg)
        if float(msg) > HUMIDITY_UPPERLIMIT or float(msg) < HUMIDITY_LOWERLIMIT:
            paho_client.publish(CLIENT_TOPIC_LED2, STATUS_ON)
            adafruit_client.publish(ADAFRUIT_LED2_FEED, STATUS_ON)
    # Operate the Buzzer based on presence of fire
    if message.topic == CLIENT_TOPIC_FLAME and msg == STATUS_HIGH:
        adafruit_client.publish(ADAFRUIT_FIRE_FEED, 0)
        adafruit_client.publish(ADAFRUIT_BUZZER_FEED, STATUS_ON)
        paho_client.publish(CLIENT_TOPIC_BUZZER, STATUS_ON)
        # print('Fire in the system')
    if message.topic == CLIENT_TOPIC_FLAME and msg == STATUS_LOW:
        adafruit_client.publish(ADAFRUIT_FIRE_FEED, 1)

# Message function will be called when a subscribed feed of Adafruit IO has a new value.
# The feed parameter identifies the feed, and 
# the payload parameter has the new value.
def on_ada_message(client, feed, payload):
    print('--> Topic \'{0}\' received new value from Adafruit IO: {1}'.format(feed, payload))
    if feed == ADAFRUIT_LED1_FEED:
        paho_client.publish(CLIENT_TOPIC_LED1, payload)
        print('Published to ', CLIENT_TOPIC_LED1)
    if feed == ADAFRUIT_LED2_FEED:
        paho_client.publish(CLIENT_TOPIC_LED2, payload)
        print('Published to ', CLIENT_TOPIC_LED2)
    if feed == ADAFRUIT_BUZZER_FEED:
        paho_client.publish(CLIENT_TOPIC_BUZZER, payload)

# Main 
# Main function is called when the scipt is executed 
if __name__ == '__main__':
    delay = 1
    try:
        adafruit_client.on_disconnect = on_disconnect
        adafruit_client.on_message    = on_ada_message

        paho_client.on_message = on_message 
        paho_client.on_disconnect = on_disconnect 
        
        # Connect to the server.
        paho_client.connect(CLIENT_ADDRESS, CLIENT_PORT)
        adafruit_client.connect()
        adafruit_client.loop_background()

        # Subscribe to all topics
        paho_client.subscribe(CLIENT_TOPIC_TEMPERATURE)
        paho_client.subscribe(CLIENT_TOPIC_HUMIDITY)
        paho_client.subscribe(CLIENT_TOPIC_FLAME)
        adafruit_client.subscribe(ADAFRUIT_LED1_FEED)
        adafruit_client.subscribe(ADAFRUIT_LED2_FEED)
        paho_client.loop_forever()
        while gateway_status:
            # Wait for 'delay' sec
            time.sleep(delay)       
        print('outside loop')  
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
    except Exception as e:
        print('Interrupt Caused by: \n', e)
    finally:
        print('Cleanup')
        paho_client.disconnect()

