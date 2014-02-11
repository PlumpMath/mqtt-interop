import mqtt.client, socket, pickle, time, logging

class Callbacks(mqtt.client.Callback):

  def __init__(self):
    self.messages = []
    self.publisheds = []
    self.subscribeds = []
    self.unsubscribeds = []

  def clear(self):
    self.__init__()

  def connectionLost(self, cause):
    logging.info("connectionLost %s", str(cause))

  def publishArrived(self, topicName, payload, qos, retained, msgid):
    logging.info("publishArrived %s %s %d %d %d", topicName, payload, qos, retained, msgid)
    self.messages.append((topicName, payload, qos, retained, msgid))
    return True

  def published(self, msgid):
    logging.info("published %d", msgid)
    self.publisheds.append(msgid)

  def subscribed(self, msgid):
    logging.info("subscribed %d", msgid)
    self.subscribeds.append(msgid)

  def unsubscribed(self, msgid):
    logging.info("unsubscribed %d", msgid)
    self.unsubscribeds.append(msgid)

host = "dds"
port = 1883

device = pickle.load(open('xiv.dat','rb')).pop()

aclient = mqtt.client.Client("myclientid".encode("utf-8"))
callback = Callbacks()
aclient.registerCallback(callback)

aclient.connect(host=host, port=port,
                username=device['username'],
                password=device['password'])
aclient.subscribe(device['topics'], [0, 0])
aclient.publish(device['topics'].pop(), b"qos 0")
time.sleep(1)
aclient.disconnect()

print(callback.messages)
