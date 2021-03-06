"""
*******************************************************************
  Copyright (c) 2013, 2014 IBM Corp.
 
  All rights reserved. This program and the accompanying materials
  are made available under the terms of the Eclipse Public License v1.0
  and Eclipse Distribution License v1.0 which accompany this distribution. 
 
  The Eclipse Public License is available at 
     http://www.eclipse.org/legal/epl-v10.html
  and the Eclipse Distribution License is available at 
    http://www.eclipse.org/org/documents/edl-v10.php.
 
  Contributors:
     Ian Craggs - initial implementation and/or documentation
*******************************************************************
"""

import mbt, sys, mqtt, glob, time, logging, getopt, os

import MQTTV311_spec, client_test

def socket_check(a, b):
	# <socket.socket object, fd=3, family=2, type=1, proto=0>
	awords = str(a).split()
	del awords[2]
	astr = ''.join(awords)
	bwords = str(b).split()
	del bwords[2]
	bstr = ''.join(bwords)
	#print("checking sockets", astr, "and", bstr)
	return astr == bstr

def exception_check(a, b):
	return True

def cleanup(hostname="localhost", port=1883):
	logging.info("Cleaning up")
	# clean all client state
	clientids = ("", "normal", "23 characters4567890123", "A clientid that is too long - should fail")

	for clientid in clientids:
		aclient = mqtt.client.Client("myclientid".encode("utf-8"))
		aclient.connect(host=hostname, port=port, cleansession=True,
				username=username, password=password)
		time.sleep(.1)
		aclient.disconnect()
		time.sleep(.1)

	# clean retained messages 
	callback = client_test.Callbacks()
	aclient = mqtt.client.Client("clean retained".encode("utf-8"))
	aclient.registerCallback(callback)
	aclient.connect(host=hostname, port=port, cleansession=True,
			username=username, password=password)
	#TODO: make use of disable_wildcard_topics here
	aclient.subscribe(["#"], [0])
	time.sleep(2) # wait for all retained messages to arrive
	for message in callback.messages:  
		if message[3]: # retained flag
		  aclient.publish(message[0], b"", 0, retained=True)
	aclient.disconnect()
	time.sleep(.1)

	MQTTV311_spec.client.__init__()
	logging.info("Cleaned up")


if __name__ == "__main__":
	try:
		opts, args = getopt.gnu_getopt(sys.argv[1:], "t:d:h:p:",
                    ["testname=", "testdir=", "testdirectory=", "hostname=",
                      "port=", "username=", "password=", "topics=",
		      "disable_wildcards", "zero_length_clientid"])
	except getopt.GetoptError as err:
		print(err) # will print something like "option -a not recognized"
		sys.exit(2)

	testname = testdirectory = None
	hostname = "localhost"
	port = 1883
	username = None
	password = None
	for o, a in opts:
		if o in ("--help"):
			print("Not yet implemented.");
			sys.exit()
		elif o in ("-t", "--testname"):
			testname = a
		elif o in ("-s", "--testdir", "--testdirectory"):
			testdirectory = a
		elif o in ("-h", "--hostname"):
			hostname = MQTTV311_spec.hostname = a
		elif o in ("-p", "--port"):
			port = MQTTV311_spec.port = int(a)
		elif o in ("--username"):
			username = a
			MQTTV311_spec.usernames = (a,)
		elif o in ("--password"):
			password = a
			MQTTV311_spec.passwords = (a,)
		elif o in ("--topics"):
			MQTTV311_spec.topics = tuple(a.split(","))
		elif o in ("--disable_wildcards"):
			MQTTV311_spec.disable_wildcard_topics = True
		elif o in ("--zero_length_clientid"):
			MQTTV311_spec.zero_length_clientid = True
		else:
			assert False, "unhandled option"

	MQTTV311_spec.setup()

	if testname:
		testnames = [testname]

	if testdirectory:
		testnames = glob.glob(testdirectory+os.sep+"*")

	testnames.sort(key=lambda x: int(x.split(".")[-1])) # filename index order
	cleanup(hostname, port)
	for testname in testnames:
		checks = {"socket": socket_check, "exception": exception_check}
		MQTTV311_spec.test = mbt.Tests(mbt.model, testname, checks, 
				observationMatchCallback = MQTTV311_spec.observationCheckCallback,
				callCallback = MQTTV311_spec.callCallback)
		MQTTV311_spec.test.run(stepping=False)
		cleanup(hostname, port)

