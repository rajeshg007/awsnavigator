class baseModule:

	def setup(self, session):
		self.client = session.client(self.moduleName)
		self.resource = session.resource(self.moduleName)
		self.starterFunctions()

	def getServiceName(self):
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