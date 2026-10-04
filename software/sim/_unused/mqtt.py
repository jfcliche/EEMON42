    async def mqtt_connect_and_subscribe(self):


        def sub_cb(topic, msg):
            print((topic, msg))
            if topic == b'notification' and msg == b'received':
                print('ESP received hello message')


        try:
            print(f'Starting MQTT connection')
            config = self.config

            # Make sure wifi link is ready
            while not self.station:
                print('MQTT client waiting for WiFi connection')
                await asyncio.sleep(1)
            print(f'Creating MQTT object')

            client = MQTTClient(self.client_id, 
                config['mqtt_server'], 
                user=config['mqtt_user'], 
                password=config['mqtt_password'])
            print('MQTT object created. Connecting...')
            client.set_callback(sub_cb)
            client.connect()
            print('MQTT connection complete. Subscribing...')
            client.subscribe(self.topic_sub)
            print('Connected to %s MQTT broker, subscribed to %s topic' %
                  (config['mqtt_server'], topic_sub))
            self.client = client  # Store MQTT client object, which also indicates it is fully ready 
        except Exception as e:
            print(f'Error while connecting to MQTT server: {repr(e)}')
            # self.fatal_error = True
            raise

    async def process_mqtt_messages(self):
        """ Continuously look for new data to send and sent it when available 
        """
        counter = 0
        while True:
            try:
                counter += 1
                if self.client: # don't do anything unless the MQTT client is up and running
                    self.client.check_msg()  # what does that do? messages from server?
                    msg = json.dumps({"counter": counter})
                    self.client.publish(self.topic_pub, msg)
                await asyncio.sleep(self.message_interval)
            except OSError as e:
                self.fatal_error = True

    def restart_and_reconnect(self):
        print('Failed to connect to MQTT broker. Reconnecting...')
        time.sleep(10)
        machine.reset()