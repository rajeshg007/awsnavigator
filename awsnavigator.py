#!/usr/bin/python
import boto3
import sys
import re
import argparse
from importlib.machinery import SourceFileLoader
import traceback

supportedServices = ['s3']
selectedService = ''
presentPath = []
session = None
region = None
module = None

def readInput(*args):
	try:
		raw_input = ""
		prompt = args[0]
		commands = args[1]
		commands.append('exit')
		regExp = "^(" + "|".join(commands) + ")$"
		exp = re.compile(regExp)

		while True:
			raw_input = input(prompt)
			raw_input = raw_input.strip()
			if raw_input == "":
				print("Please enter a valid command from the list ("+", ".join(commands)+")")
				continue

			words = re.split('\s+', raw_input)
			m = exp.search(words[0])
			if words[0] == 'exit':
				print('Exiting the Navigator')
				sys.exit()

			if m:
				return words

			if raw_input != "":
				print("Invalid input: " + raw_input)
				print("Please enter a valid command from the list ("+", ".join(commands)+")")

	except Exception as e:
		raise e

def getRelatedObject (selectedService):
	module = SourceFileLoader(selectedService,"classes/%s.py" % (selectedService)).load_module()
	class_ = getattr(module, selectedService)
	instance = class_()
	return instance

def isValidRegion(region, service):
	if region in session.get_available_regions(service):
		return True
	else:
		return False

def main(args):
	global session
	global region
	global selectedService
	global presentPath
	global module

	try:

		session = boto3.Session(profile_name=args.profile)

		if session.region_name or args.region !='':
			pass
		else:
			print('Please Update region in AWS Config or pass it as a Parameter to AWSNavigator')
			sys.exit()

		region = session.region_name if args.region == 'None' else args.region

		while True:
			if selectedService == '':
				Service = readInput('Select Service :', supportedServices)
				selectedService = Service[0]
				if isValidRegion(region,selectedService):
					pass
				else:
					print("%s is not present in %s, defaulting to %s" % (Service[0],args.region,session.region_name))
			try:
				if module.getServiceName() != selectedService:
					module = getRelatedObject(selectedService)
					module.setup(session)
			except Exception as e:
				if format(e) == "'NoneType' object has no attribute 'getServiceName'":
					module = getRelatedObject(selectedService)
					module.setup(session)
				else:
					print(e)
			params = readInput("%s:/%s :" % (selectedService, "/".join(presentPath)), module.supportedCommands())
			module.call(presentPath,params)
			presentPath = module.returnParams('presentPath')
			selectedService = module.returnParams('selectedService')

	except Exception as e:
		raise e

try:
	if __name__ == "__main__":
		if sys.platform not in ['darwin']:
			raise Exception("OS not Supported")
		parser = argparse.ArgumentParser(description='AWS Navigator')
		parser.add_argument('--profile', dest='profile',type=str,default='default',help='AWS Profile')
		parser.add_argument('--region', dest='region',type=str,default='None',help='AWS Region Name')
		args = parser.parse_args()
		main(args)
except Exception as e:
	print(e)
	traceback.print_exc()