import time
import RPi.GPIO as GPIO
import paho.mqtt.client as paho
import Adafruit_DHT

# GPIO pins
LED1 = 26
LED2 = 19
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 2
BUZZER = 22
FLAME = 6

# Gateway Info
BROKER_ADDRESS = "192.168.1.215"
# BROKER_ADDRESS = "192.168.2.42"
BROKER_PORT = 1883

# MQTT Topic
TOPIC_LED1 = "led1temp"
TOPIC_LED2 = "led2hum"
TOPIC_HUMIDITY = "sensorhum"
TOPIC_TEMPERATURE = "sensortemp"
TOPIC_BUZZER = "buzz"
TOPIC_FLAME = "sensorflame"

client_status = True
STATUS_OFF ="OFF"
STATUS_ON = "ON"
STATUS_HIGH ="HIGH"
STATUS_LOW ="LOW"

def led_on(led_pin):
    GPIO.output(led_pin, GPIO.HIGH)

def led_off(led_pin):
    GPIO.output(led_pin, GPIO.LOW)

def buzzer_on(pin):
    GPIO.output(pin, GPIO.HIGH)

def buzzer_off(pin):
    GPIO.output(pin, GPIO.LOW)

# Function will be called when Client is disconnected    
def on_disconnect(client, userdata, message):
    print('Client Disconnected from Gateway')

# Function will be called when a subscribed topic has a new value
def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    print("message received " ,msg)
    print("message topic=",message.topic)
    # Operate the LED based on Temperature and Humidity level
    if message.topic == TOPIC_LED1 and msg == STATUS_ON:
        led_on(LED1)
    elif message.topic == TOPIC_LED1 and msg == STATUS_OFF:
        led_off(LED1)

    # Operate buzzer based on warning signal
    if message.topic == TOPIC_BUZZER and msg == STATUS_ON:
        buzzer_on(BUZZER)
    elif message.topic == TOPIC_BUZZER and msg == STATUS_OFF:
        buzzer_off(BUZZER)   

def setup():
    # Using Broadcom SOC Channel mode (GPIO numbering)
    GPIO.setmode(GPIO.BCM)
    # LEDs are set to Output 
    GPIO.setup(LED1, GPIO.OUT)
    GPIO.setup(LED2, GPIO.OUT)
    GPIO.setup(FLAME, GPIO.IN)
    # Create a new Instance
    client = paho.Client("C1")
    return client

#Main 
if __name__ == '__main__':
    delay = 4
    try:
        paho_client = setup()  
        paho_client.on_message = on_message 
        paho_client.on_disconnect = on_disconnect 
        
        # Connect to the Gateway server.
        paho_client.connect(BROKER_ADDRESS, BROKER_PORT)
        # Start loop
        paho_client.loop_start()
        print('Subscribing to topics: {0}, {1}'.format(TOPIC_LED1, TOPIC_LED2))
        paho_client.subscribe(TOPIC_LED1)
        paho_client.subscribe(TOPIC_LED2)
        while client_status:
            humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
            print('Publishing message to topics: {0}, {1}'.format(TOPIC_TEMPERATURE, TOPIC_HUMIDITY))
            if humidity is not None:
                # print("Humidity={0}%".format(humidity))
                paho_client.publish(TOPIC_HUMIDITY,humidity)
            if temperature is not None:
                # print("Temp={0}C ".format(temperature))
                paho_client.publish(TOPIC_TEMPERATURE,temperature)
            if GPIO.input(FLAME) == GPIO.HIGH:
                print('Publishing message to topic: {0}'.format(TOPIC_FLAME))
                print('Fire Warning. Publishing message to topic: {0}'.format(TOPIC_FLAME))
                paho_client.publish(TOPIC_FLAME,STATUS_HIGH)
            if GPIO.input(FLAME) == GPIO.LOW:
                print('Publishing message to topic: {0}'.format(TOPIC_FLAME))
                print('No Fire')
                paho_client.publish(TOPIC_FLAME,STATUS_LOW)
            # Wait for 'delay' sec
            time.sleep(delay)         
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
    except:
        print('Interrupt ')
    finally:
        print('Cleanup')
        paho_client.disconnect()
        paho_client.loop_stop()
        GPIO.cleanup()
