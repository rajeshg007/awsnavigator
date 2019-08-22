from importlib.machinery import SourceFileLoader
import re
import os
import json
module = SourceFileLoader("","classes/base.py").load_module()
class_ = getattr(module, 'baseModule')

class asg (class_):
	moduleName = 'autoscaling'
	serviceName = 'asg'
	selectedService = 'asg'
	presentPath = []

	emptyPathFunctions = {
		'list': 'listASG',
		'ls': 'listASG',
		'open': 'openASG',
		"refresh": "reloadASGs",
		}

	PathFunctions = {
		"show": "showProperty",
		'update': 'updateASG',
		'close': 'closeASG',
		"refresh": "reloadASGs",
		}

	def reloadASGs(self):
		instances =  self.fetchASG()
		if len(self.presentPath) > 0:
			print("previously selected asg was : "+ self.presentPath[0])
			print("Trying to open it again")
		self.params = ["open", self.presentPath[0]]
		self.presentPath = []
		self.openASG()		

	def openASG(self):
		if len(self.params) <= 1:
			print("Insufficient Params")
			return False
		else:
			if self.params[1] in self.fetchASG().keys():
				self.presentPath.append(self.params[1])

	def closeASG(self):
		self.presentPath = []

	def updateASG(self):
		updateableParmas = {
		"minsize":{"type":0, "value":"MinSize"},
		"maxsize":{"type":0, "value":"MaxSize"},
		"desiredcapacity":{"type":0, "value":"DesiredCapacity"},
		"healthchecktype":{"type":"EC2", "value":"HealthCheckType"},
		}
		if len(self.params) <=1:
			print("Insufficient Params")
			return false
		else:
			params = self.params[1].split(":")
			if len(params) > 1:
				if params[0].lower() in updateableParmas.keys() and self.isTypeCastable(updateableParmas[params[0].lower()]['type'],params[1].strip()):
					botoParams = {}
					botoParams['AutoScalingGroupName']=self.presentPath[0]
					botoParams[updateableParmas[params[0].lower()]['value']]=type(updateableParmas[params[0].lower()]['type'])(params[1].strip())
					val = self.client.update_auto_scaling_group(**botoParams)
			else:
				print("Available Params: "+",".join(updateableParmas.keys()))

	def showProperty(self):
		main = self.fetchASG()[self.presentPath[0]]
		if len(self.params) == 1:
			print("Available properties : "+", ".join([key for key in main.keys()]))
		else:
			propertythread = self.params[1].split("/")
			for item in propertythread:
				if item.lower() not in [key.lower() for key in main.keys()]:
					print(item+" not found in the asg" + self.presentPath[0])
					return False
				for key in main.keys():
					if item.lower() == key.lower():
						main = main[key]
						break
			print(json.dumps(main))
			
	def listASG(self):
		asgs = self.fetchASG()
		for asg in asgs.keys():
			print(asg)

	def fetchASG(self):
		if self.returnParams("asgs"):
			return self.returnParams("asgs")
		else:
			items = self.client.describe_auto_scaling_groups()['AutoScalingGroups']
			asgs = {}
			for item in items:
				asgs[item['AutoScalingGroupName']] = item
		self.asgs = asgs
		return asgs

	def setup(self, session):
		self.client = session.client(self.moduleName)
		self.starterFunctions()