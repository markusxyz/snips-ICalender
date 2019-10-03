#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
from urllib.request import urlopen
import datetime

CONFIG_INI = "config.ini"

# If this skill is supposed to run on the satellite,
# please get this mqtt connection info from <config.ini>
# Hint: MQTT server is always running on the master device
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

class ICalender(object):
    """Class used to wrap action code with mqtt connection
        
        Please change the name refering to your application
    """

    def __init__(self):
                # get the configuration if needed
        try:
                self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
                self.url =  self.config.get("secret").get("url")
        except :
                self.config = None

        # start listening to MQTT
        self.start_blocking()
        
    # --> Sub callback function, one per intent
    def intent_1_callback(self, hermes, intent_message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")
        
        # action code goes here...
        print('[Received] intent: {}'.format(intent_message.intent.intent_name))
        c = urlopen(self.url).read().decode()
        print (self.url)
        startstop = False
        tree = []

        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(1)
        yesterday = today + datetime.timedelta(-1)

        datum = today.strftime("%Y%m%d")

        say = ''

        for line in c.splitlines():
    
                liste = line.split(':')

                if ( liste[0] == 'BEGIN' and liste[1] == 'VEVENT'):
                        startstop = True
                        tupel = []
        
                if ( liste[0] == 'END' and liste[1] == 'VEVENT'):
                        startstop = False
                        tree.append(tupel)
        
                if ( startstop ):
                        if ( len(liste) > 1 ):
                                tupel.append(liste[1])
        for each in tree:

                if ( each[4].startswith(datum)):
                        
                        zeit = each[4].split('T')
                        zeit = str(zeit[1])

                        say = say + ' ' + each[7] + ' ' + zeit[0:2] + ":" + zeit[3:5] + " Uhr"
                        print (say)

        # if need to speak the execution result by tts
        hermes.publish_start_session_notification(intent_message.site_id, say, "")

    # More callback function goes here...

    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        coming_intent = intent_message.intent.intent_name
        if coming_intent == 'Keeper37:askCalender':
            self.intent_1_callback(hermes, intent_message)

        # more callback and if condition goes here...

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()

if __name__ == "__main__":
    ICalender()
