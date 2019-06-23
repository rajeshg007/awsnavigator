from importlib.machinery import SourceFileLoader
import re
import os

module = SourceFileLoader("","classes/base.py").load_module()
class_ = getattr(module, 'baseModule')

class s3 (class_):
	moduleName = 's3'
	selectedService = 's3'
	presentPath = []
	buckets = []
	bucketsFetched = False
	bucket = ''
	items = []

	emptyPathFunctions = {
		'list': 'listBuckets',
		'open': 'openBucket', 
		'cd': 'changePath',
		'ls': 'listBuckets'
		}

	PathFunctions = {
		'list': 'listObjects',
		'cd': 'changePath',
		'ls': 'listObjects',
		'presign': 'preSign'
		}

	def openBucket(self):
		try:
			if self.params[1].count('/') == 0:
				bucket = self.params[1]
			else:
				firstItem = self.params[1].find('/')
				bucket = self.params[1][0:firstItem]
				key = self.params[1][firstItem+1:]
				print("%s,%s" % (bucket,key))
				print(len(key))
		except IndexError as error:
			print('path not found')
		except Exception as e:
			raise e

	def starterFunctions(self):
		return True

	def fetchBuckets(self):
		buckets = self.client.list_buckets()
		for bucket in buckets['Buckets']:
			self.buckets.append(bucket['Name'])
		self.bucketsFetched = True

	def getFunction(self, command):
		if len(self.presentPath) == 0:
			function = self.emptyPathFunctions.get(command,'none')
			return getattr(self, function)
		else:
			function = self.PathFunctions.get(command,'none')
			return getattr(self, function)


	def call(self,presentPath,params):
		self.presentPath = presentPath
		self.params = params
		print(params)
		function_ = self.getFunction(params[0])
		function_()

	def returnParams(self, param):
		return getattr(self, param)

	def supportedCommands(self):
		if len(self.presentPath) == 0:
			return list(self.emptyPathFunctions.keys())
		else:
			return list(self.PathFunctions.keys())

	def changePath (self):
		if len(self.params) >= 2:
			if self.params[1] == '..':
				try:
					self.presentPath.pop()
				except IndexError as error:
					print('Already present at root, cant go back further')
				except Exception as e:
					print(e)
			elif self.params[1] == '/':
				self.presentPath = []
			elif self.params[1].count('/') > 0:
				items = re.split('/',self.params[1])
				for item in items:
					if self.verifyPath(item):
						self.presentPath.append(item)
					else:
						print("Path not found after s3://"+"/".join(self.presentPath))
			else:
				if self.verifyPath(self.params[1]):
					self.presentPath.append(self.params[1])
				else:
					print("Path not found after s3://"+"/".join(self.presentPath))
		
		if self.bucket == "" and len(self.presentPath) > 0:
			self.bucket = self.presentPath[0]
		if len(self.presentPath) == 0:
			self.bucket = ""


	def listObjects(self):
		command = "aws s3 ls s3://"+"/".join(self.presentPath)+"/"
		output = os.popen(command).read().split("\n")
		for item in output:
			print(item.strip())
		# output = [item.strip() for item in output]

	def verifyPath(self, item):
		command = "aws s3 ls s3://"+"/".join(self.presentPath+[item])
		output = os.popen(command).read()
		print(output)
		if output != "":
			return True
		else:
			return False
	def listBuckets(self):
		self.fetchBuckets()
		for bucket in self.buckets:
			print(bucket)

	def getBucketRegion(self):
		self.resource.meta.client.get_bucket_location(Bucket=self.bucket)["LocationConstraint"]

	def preSign(self):
		if len(self.params) > 1:
			command = "aws s3 presign "+"/".join(self.presentPath)+"/"+self.params[1] + " --region " + self.resource.meta.client.get_bucket_location(Bucket=self.bucket)["LocationConstraint"]
			output = os.popen(command).read()
			print(output)
		else:
			print("insufficient arguments, format: presign <itemname>, note: item should be present in current folder")

