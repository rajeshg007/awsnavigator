#!/usr/bin/python
import boto3
import sys
import re
import argparse
from importlib.machinery import SourceFileLoader
import traceback

supportedServices = ['s3', 'ec2', "elasticsearch"]
selectedService = ''
presentPath = []
session = None
region = None
module = None
systemCommands = ["exit", "change"]
def readInput(*args):
	try:
		raw_input = ""
		prompt = args[0]
		commands = args[1]
		commands.append('change')
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

def change(words):
	global session
	global region
	global selectedService
	global presentPath
	global module
	if len(words) >= 3 and words[1] == "region":
		if words[2] == region:
			print("Already Present in "+ words[2])
			return True
		session = boto3.Session(profile_name=session.profile_name, region_name=words[2])
		print("changed to "+session.region_name)
		module = getRelatedObject(selectedService)
		module.setup(session)
		presentPath = []
		region = words[2]
	elif len(words) >= 3 and words[1] == "service":
		if selectedService == words[2]:
			print("Already in Service")
			return True
		selectedService = words[2]
		module = getRelatedObject(selectedService)
		module.setup(session)
		presentPath = []
		region = words[2]
	else:
		print("Unknown command. Please try again")



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

		session = boto3.Session(profile_name=args.profile, region_name=args.region)

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
			if params[0] in systemCommands:
				if params[0] == "change":
					change(params)
			else:
				try:
					module.call(presentPath,params)
					presentPath = module.returnParams('presentPath')
					selectedService = module.returnParams('selectedService')
				except Exception as e:
					print(e)

	except Exception as e:
		raise e

try:
	if __name__ == "__main__":
		if sys.platform not in ['darwin']:
			raise Exception("OS not Supported")
		parser = argparse.ArgumentParser(description='AWS Navigator')
		parser.add_argument('--profile', dest='profile',type=str,default='default',help='AWS Profile')
		parser.add_argument('--region', dest='region',type=str,default='ap-south-1',help='AWS Region Name')
		args = parser.parse_args()
		main(args)
except Exception as e:
	print(e)
	traceback.print_exc()