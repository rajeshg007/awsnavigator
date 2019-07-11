from importlib.machinery import SourceFileLoader
import re
import os

module = SourceFileLoader("","classes/base.py").load_module()
class_ = getattr(module, 'baseModule')

class ec2 (class_):
	moduleName = 'ec2'
	selectedService = 'ec2'
	presentPath = []
	buckets = []
	bucketsFetched = False
	bucket = ''
	items = []

	emptyPathFunctions = {
		'list': 'listDomains',
		}
	PathFunctions = {
		}
	def listDomains(self):
		
	def supportedCommands(self):
		if len(self.presentPath) == 0:
			return list(self.emptyPathFunctions.keys())
		else:
			return list(self.PathFunctions.keys())
