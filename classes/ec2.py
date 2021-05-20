from importlib.machinery import SourceFileLoader
import re
import os
from functools import reduce
import numpy

module = SourceFileLoader("","classes/base.py").load_module()
class_ = getattr(module, 'baseModule')

class ec2 (class_):
	moduleName = 'ec2'
	selectedService = 'ec2'
	serviceName = 'ec2'
	presentPath = []
	items = []

	emptyPathFunctions = {
		'list': 'listInstances',
		'show': 'listInstances',
		'ls': 'listInstances',
		"open": "selectInstance",
		"refresh": "reloadInstances",
		"terminate": "terminateInstances",
		"stats": "getInstanceStats",
		"print": "printItem",
		"price": "pricing"
		}

	PathFunctions = {
			"show": "showProperty",
			"close": "unSelectInstance",
			"refresh": "reloadInstances",
			"modify": "modifyParams",
			"open": "openItems",
			"terminate": "terminateInstances",
			"forceterminate": "forceTerminateInstance",
			"restart": "restart"
		}

	def starterFunctions(self):
		self.region = self.client.meta.region_name
		self.zones = list(map((lambda x: x["ZoneName"]), self.client.describe_availability_zones()['AvailabilityZones']))

	def pricing(self):
		if len(self.params) <= 2 or len(self.params) > 3:
			print("Wrong Usage")
			print("Usage: price <lifecycle type> <instance type>")
		else:
			if self.params[1] != 'spot':
				print("under construction please try sometime later")
			else:
				response = self.client.describe_spot_price_history(
					InstanceTypes=[self.params[2]],MaxResults=1)

	def getInstanceStats(self):
		instances = self.getInstances()
		instances = list(instances.values())[0:len(instances)]
		print("Total Instance Count = "+str(len(instances)))
		print("-"*10+"LifeCycleType"+"-"*10)
		types = list(map((lambda x: x["InstanceLifecycle"] if "InstanceLifecycle" in x else "OnDemand"), instances))
		unique, counts = numpy.unique(types, return_counts=True)
		lifeCycleTypes = dict(zip(unique, counts))
		for key in lifeCycleTypes.keys():
			print(f"Total {key} Instances: {lifeCycleTypes[key]}")
		print("-"*10+"InstanceType"+"-"*10)
		types = list(map((lambda x: x["InstanceType"]), instances))
		unique, counts = numpy.unique(types, return_counts=True)
		instanceTypeCounts = dict(zip(unique, counts))
		for key in instanceTypeCounts.keys():
			print(f"Total {key} Instances: {instanceTypeCounts[key]}")


	def modifyParams(self):
		if len(self.params) > 1:
			params = self.params[1].split(":")
			
	def terminateInstances(self):
		if len(self.params) == 1 and self.returnParams("selectedInstance"):
			self.client.terminate_instances(InstanceIds=[self.returnParams("selectedInstance")])
			self.presentPath = []
			del self.selectedInstance
		elif len(self.params) > 1 and not self.returnParams("selectedInstance"):
			self.client.terminate_instances(InstanceIds=self.params[1:])
			if self.returnParams("selectedInstance") in self.params[1:] or len(self.presentPath)>0:
				self.presentPath = []
				del self.selectedInstance
		else:
			print("Insufficient parameters for terminate command")

	def forceTerminateInstance(self):
		if len(self.params) == 1 and self.returnParams("selectedInstance"):
			self.client.modify_instance_attribute(InstanceId=self.returnParams("selectedInstance"), DisableApiTermination={'Value': False })
			self.client.terminate_instances(InstanceIds=[self.returnParams("selectedInstance")])
			self.presentPath = []
			del self.selectedInstance
		else:
			print("Wrong parameters for Force Terminate command")

	def openItems(self):
		if len(self.params) == 2 :
			if self.params[1].startswith("sg-") and self.params[1] in self.getInstance(self.selectedInstance)["sg"].values():
				self.openSG(self.params[1])
			else:
				print("something is wrong")
		else:
			print("unrecognized command")
		pass

	def openSG(self, sg):
		if sg in self.getInstance(self.selectedInstance)["sg"].keys():
			sg = self.getInstance(self.selectedInstance)["sg"][sg]
		self.sg = self.resource.SecurityGroup(sg)
		self.presentPath.append(sg)
		print(self.presentPath)

	def reloadInstances(self):
		instances =  self.fetchInstances()
		if len(self.presentPath) > 0:
			print("previously selected instance is : "+ self.selectedInstance)
			del self.selectedInstance
		self.presentPath = []

	def unSelectInstance(self):
		self.presentPath = []
		del self.selectedInstance

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
			print("Available properties : "+", ".join([key for key in main.keys()]))
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

	def restart(self):
		output = self.client.reboot_instances(InstanceIds= [self.selectedInstance])
		print(output)


	def fetchInstances(self):
		self.reservations = self.client.describe_instances(Filters=[{"Name":"instance-state-name","Values":['pending','running','stopped']}])["Reservations"]
		self.instances = {}
		for reservation in self.reservations:
			for instance in reservation["Instances"]:
				if 'Tags' in instance:
					tags = instance['Tags']
					tagkeys = []
					tagvalues = []
					for tag in tags:
						tagkeys.append(tag["Key"].lower())
						tagvalues.append(tag["Value"])
					tags = dict(zip(tagkeys, tagvalues))
					instance['Tags'] = tags
					instance["sg"] = {}
					for sg in instance["SecurityGroups"]:
						instance["sg"][sg["GroupName"]] = sg["GroupId"]
				self.instances[instance["InstanceId"]] = instance
		return self.instances
	
	def getInstances(self):
		instances = self.returnParams("instances")
		if not instances:
			instances = self.fetchInstances()
		return instances

	def listInstances(self):
		instances = self.getInstances()
		for key, value in instances.items():
			if len(self.params) > 1:
				if self.matchInstance(value, self.params[1:]):
					print(key+" "+ (value["Tags"]["Name".lower()] if "Name".lower() in value["Tags"] else key) +" "+ value["State"]["Name"]+" "+ (value["PublicIpAddress"] if "PublicIpAddress" in value.keys() else "") + " " + (value["PrivateIpAddress"] if "PrivateIpAddress" in value.keys() else "")+ " " + (str(value["LaunchTime"]) if "LaunchTime" in value.keys() else ""))
			else:
				print(key+" "+ (value["Tags"]["Name".lower()] if "Tags" in value and "Name".lower() in value["Tags"] else key) +" "+ value["State"]["Name"]+" "+ (value["PublicIpAddress"] if "PublicIpAddress" in value.keys() else "") + " " + (value["PrivateIpAddress"] if "PrivateIpAddress" in value.keys() else ""))
	
	def matchInstance(self, instance, params):
		params = self.params[1:]
		retVal = False
		for param in params:
			splitParams = param.split(":")
			if splitParams[0] == "tag":
				if splitParams[1].lower() in instance["Tags"].keys():
					if instance["Tags"][splitParams[1]] == splitParams[2]:
						retVal = True
					else:
						return False
			else:
				if splitParams[0] in instance and instance[splitParams[0]] == splitParams[1]:
					retVal = True
				else:
					return False
		return retVal