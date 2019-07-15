from importlib.machinery import SourceFileLoader
import re
import os

module = SourceFileLoader("","classes/base.py").load_module()
class_ = getattr(module, 'baseModule')

class elasticsearch (class_):
	moduleName = 'es'
	serviceName = 'elasticsearch'
	selectedService = 'elasticsearch'
	presentPath = []
	emptyPathFunctions = {
		'list': 'listDomains',
		"refresh": "reloadDomains",
		"open": "selectDomain",
		}

	PathFunctions = {
		"refresh": "reloadDomains",
		"close": "unSelectDomain",
		"show": "showProperty",
		}

	def showProperty(self):
		main = self.getDomain(self.presentPath[0])
		if len(self.params) == 1:
			print("Available properties : "+", ".join([key for key in main.keys()]))
		else:
			propertythread = self.params[1].split("/")
			for item in propertythread:
				if item.lower() not in [key.lower() for key in main.keys()]:
					print(item+" not found in the Domain" + self.presentPath[0])
					return False
				for key in main.keys():
					if item.lower() == key.lower():
						main = main[key]
						break
			print(main)
	
	def getDomain(self, key):
		return self.getDomains()[key]

	def unSelectDomain(self):
		self.presentPath = []

	def selectDomain(self):
		domains = self.getDomains()
		if self.params[1] in domains.keys():
			self.presentPath = [self.params[1]]
		else:
			print("Domain not found")

	def listDomains(self):
		domains = self.getDomains()
		for domain in domains.keys():
			print(domains[domain]["DomainName"]+"\t"+domains[domain]["Endpoints"]["vpc"]+"\t"+domains[domain]["ElasticsearchClusterConfig"]["InstanceType"]+"\t"+str(domains[domain]["ElasticsearchClusterConfig"]["InstanceCount"]))

	def reloadDomains(self):
		if self.returnParams("domains"):
			del self.domains
			self.presentPath = []
		self.listDomains()

	def getDomains(self):
		if self.returnParams("domains"):
			return self.returnParams("domains")
		else:
			domains = self.client.list_domain_names()
			domainList = [domain["DomainName"] for domain in domains["DomainNames"]]
			domainDetails = self.client.describe_elasticsearch_domains(DomainNames=domainList)
			domains = {}
			for domainDetail in domainDetails["DomainStatusList"]:
				domains[domainDetail["DomainName"]] = domainDetail
			self.domains = domains
		return domains

	def setup(self, session):
		self.client = session.client(self.moduleName)
		self.starterFunctions()