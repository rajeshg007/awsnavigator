import json
import datetime
class baseModule:

	def setup(self, session):
		self.client = session.client(self.moduleName)
		self.resource = session.resource(self.moduleName)
		self.starterFunctions()

	def getServiceName(self):
		if self.returnParams("serviceName"):
			return self.serviceName
		else:
			return self.moduleName
	
	def call(self,presentPath,params):
		self.presentPath = presentPath
		self.params = params
		print(params)
		function_ = self.getFunction(params[0])
		function_()

	def getFunction(self, command):
		if len(self.presentPath) == 0:
			function = self.emptyPathFunctions.get(command,'none')
			return getattr(self, function)
		else:
			function = self.PathFunctions.get(command,'none')
			return getattr(self, function)

	def starterFunctions(self):
		return True

	def returnParams(self, param):
		try:
			return getattr(self, param, False)
		except:
			return False

	def supportedCommands(self):
		if len(self.presentPath) == 0:
			return list(self.emptyPathFunctions.keys())
		else:
			return list(self.PathFunctions.keys())
	def isTypeCastable(self,var1, var2):
		try:
			type(var1)(var2)
			return True
		except:
			return False
	def dateSerialization(self,o):
		if isinstance(o, datetime.datetime):
			return {"type":"date","value":o.__str__()}

	def printItem(self):
		for param in self.params:
			print(param)
			print("-"*25)
			print(json.dumps(self.returnParams(param), default = self.dateSerialization))
			print("-"*25)