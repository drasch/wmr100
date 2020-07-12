import fileinput
import json
import paho.mqtt.client as mqtt

# {"topic": "temp", "timestamp": "2020-07-11 23:24:22.636598", "sensor": 0, "smile": 0, "trend": 2, "temp": 31.6, "humidity": 45, "dewpoint": 0.0, "source": "wmr100.0", "origin": "wmr100"}
# {"topic": "clock", "timestamp": "2020-07-11 23:24:22.652776", "at": "202007111624", "powered": 0, "battery": 0, "rf": 0, "level": 1, "source": "wmr100", "origin": "wmr100"}
# {"topic": "temp", "timestamp": "2020-07-11 23:24:22.820492", "sensor": 1, "smile": 2, "trend": -1, "temp": 2.4, "humidity": 31, "dewpoint": 0.0, "source": "wmr100.1", "origin": "wmr100"}

client = mqtt.Client()
client.connect("fpp1.rbhome")


def pub(name, number, type):
	full_name = f"{name}_{type}"
	config_topic = f"homeassistant/sensor/{full_name}/config" 
	data = {"name": full_name.replace("_", " ").title(),
		"state_topic": f"diy/oregon/{number}/state",
		"value_template": f"{{{{ value_json.{type} }}}}"
		}
	if type == "temperature":
		data["device_class"] = "temperature"
		data["unit_of_measurement"] = "°C"
	elif type == "humidity":
		data["device_class"] = "humidity"
		data["unit_of_measurement"] = "%"
		

	client.publish(config_topic, json.dumps(data))

pub("garage_fridge", 1, "temperature")
pub("garage_fridge", 1, "humidity")
pub("garage_ambient", 0, "temperature")
pub("garage_ambient", 0, "humidity")

for line in fileinput.input():
	try:
		rec = json.loads(line)
		if rec.get("topic", None) == "temp":
			sensor = rec.get("sensor", -1)
			temp = rec.get("temp", None)
			humidity = rec.get("humidity", None)

			data = {}
			if temp:
				data["temperature"] = temp
			if humidity:
				data["humidity"] = humidity
			
			client.publish(f"diy/oregon/{sensor}/state", json.dumps(data))
			
	except:
		pass
