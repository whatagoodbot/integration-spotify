import os
import json
from paho.mqtt import client as mqtt_client
from dotenv import load_dotenv
from commands import relink, genre

load_dotenv()

broker = os.environ.get('MQTT_HOSTNAME')
port = int(os.environ.get('MQTT_PORT'))
environment = os.environ.get('PYTHON_ENV')
client_id = 'spotify-client'
username = os.environ.get('MQTT_USERNAME')
password = os.environ.get('MQTT_PASSWORD')
mqtt_topics = ['relink', 'genres']
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc != 0:
            print('Failed to connect, return code %d\n', rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        envLength = len(environment) + 1
        print(msg.topic[envLength:len(msg.topic)])
        payload=json.loads(str(msg.payload.decode('utf-8','ignore')))
        if msg.topic[envLength:len(msg.topic)] == 'relink':
          client.publish(f'{environment}/broadcast', json.dumps(relink(payload['trackId'], payload['meta'])))
        elif msg.topic[envLength:len(msg.topic)] == 'genres':
          client.publish(f'{environment}/broadcast', json.dumps(genre(payload['trackId'], payload['meta'])))

    for topic in mqtt_topics:
      client.subscribe(f'{environment}/{topic}')
      print(f'Subscribed to {environment}/{topic}')
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

run()
