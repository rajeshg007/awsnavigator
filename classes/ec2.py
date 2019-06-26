from importlib.machinery import SourceFileLoader
import re
import os

module = SourceFileLoader("","classes/base.py").load_module()
class_ = getattr(module, 'baseModule')

class ec2 (class_):
	moduleName = 'ec2'
	selectedService = 'ec2'
	presentPath = []
	items = []

	emptyPathFunctions = {
		'list': 'listInstances',
		'ls': 'listInstances',
		"open": "selectInstance",
		"refresh": "reloadInstances"
		}

	PathFunctions = {
			"show": "showProperty",
			"close": "unSelectInstance",
			"refresh": "reloadInstances",
			"modify": "modifyParams"
		}
	def reloadInstances(self):
		instances =  self.fetchInstances()
		if len(self.presentPath) > 0:
			print("previously selected instance is : "+ self.selectedInstance)
			del self.selectedInstance
		self.presentPath = []

	def unSelectInstance(self):
		self.presentPath = []
		del self.selectedInstance

	def supportedCommands(self):
		if len(self.presentPath) == 0:
			return list(self.emptyPathFunctions.keys())
		else:
			return list(self.PathFunctions.keys())

	def selectInstance(self):
		instances = self.getInstances()
		if self.params[1] in self.instances.keys():
			self.selectedInstance = self.params[1]
			self.presentPath = [self.params[1]]
		else:
			print("instance id not found")

	def getInstance(self, key):
		return self.getInstances()[key]

	def showProperty(self):
		main = self.getInstance(self.selectedInstance)
		if len(self.params) == 1:
			print([key for key in main.keys()])
		else:
			propertythread = self.params[1].split("/")
			for item in propertythread:
				if item.lower() not in [key.lower() for key in main.keys()]:
					print(item+" not found in the instance" + self.selectedInstance)
					return False
				for key in main.keys():
					if item.lower() == key.lower():
						main = main[key]
						break
			print(main)

	def fetchInstances(self):
		self.reservations = self.client.describe_instances()["Reservations"]
		self.instances = {}
		for reservation in self.reservations:
			for instance in reservation["Instances"]:
				tags = instance['Tags']
				tagkeys = []
				tagvalues = []
				for tag in tags:
					tagkeys.append(tag["Key"].lower())
					tagvalues.append(tag["Value"])
				tags = dict(zip(tagkeys, tagvalues))
				instance['Tags'] = tags
				self.instances[instance["InstanceId"]] = instance
		return self.instances
	def getInstances(self):
		instances = self.returnParams("instances")
		if not instances:
			instances = self.fetchInstances()
		return instances

	def listInstances(self):
		instances = self.getInstances()
		if not instances:
			instances = self.fetchInstances()
		for key, value in instances.items():
			if len(self.params) > 1:
				if self.matchInstance(value, self.params[1:]):
					print(key+" "+ value["Tags"]["Name".lower()] if "Name".lower() in value["Tags"] else key)
			else:
				print(key+" "+ value["Tags"]["Name".lower()] if "Name".lower() in value["Tags"] else key)
	
	def matchInstance(self, instance, params):
		params = self.params[1:]
		for param in params:
			splitParams = param.split(":")
			if splitParams[0] == "tag":
				if splitParams[1].lower() in instance["Tags"].keys():
					if instance["Tags"][splitParams[1]] == splitParams[2]:
						return True
			return False
		return False