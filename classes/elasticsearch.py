from importlib.machinery import SourceFileLoader
import re
import os

module = SourceFileLoader("","classes/base.py").load_module()
class_ = getattr(module, 'baseModule')

class elasticsearch (class_):
	moduleName = 'es'
	selectedService = 'elasticsearch'
	presentPath = []
	emptyPathFunctions = {
		'list': 'listDomains',
		"refresh": "reloadDomains",
		}
	PathFunctions = {
		"refresh": "reloadDomains",
		}

	def listDomains(self):
		domains = self.fetchDomains()
		for domain in domains.keys():
			print(domains[domain]["DomainName"]+"\t"+domains[domain]["Endpoints"]["vpc"]+"\t"+domains[domain]["ElasticsearchClusterConfig"]["InstanceType"]+"\t"+str(domains[domain]["ElasticsearchClusterConfig"]["InstanceCount"]))

	def reloadDomains(self):
		if self.returnParams("domains"):
			del self.domains
			self.presentPath = []
		self.listDomains()

	def fetchDomains(self):
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