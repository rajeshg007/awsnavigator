#!/usr/bin/python
import boto3
import sys
import re
import argparse


SupportedServices = ['s3']
SupportedCommands = ['list','open', 'cd', 'ls']
SupportedItems = {
	'iam': ['users'],
	's3': ['buckets']
}

SelectedService = ''
PresentPath = ''
session = None
region = None

def readInput(*args):
	try:
		input = ""

		prompt = args[0]
		commands = args[1]
		regExp = "^(" + "|".join(commands) + ")$"

		exp = re.compile(regExp)

		while True:
			input = raw_input(prompt)
			input = input.strip()

			if input == "":
				print "Please enter a valid value from the list ("+", ".join(commands)+") :"
				continue

			words = re.split('\s+', input)

			m = exp.search(words[0])

			if m:
				return words

			if input != "":
				print "Invalid input format: " + input

	except Exception as e:
		raise e

def listBuckets(session):
	client = session.client('s3')
	buckets = client.list_buckets()
	for bucket in buckets['Buckets']:
		print bucket['Name']

def isValidRegion(region, service):
	if region in session.get_available_regions(service):
		return True
	else:
		return False

def main(args):
	global session
	global region
	global SelectedService
	global PresentPath

	try:
		session = boto3.Session(profile_name=args.profile)
		if session.region_name or args.region !='None':
			pass
		else:
			print 'Please Update region in AWS Config or pass it as a Parameter to AWSNavigator'
			sys.exit()

		region = session.region_name if args.region == 'None' else args.region

		while True:
			if SelectedService == '':
				Service = readInput('Select Service :', SupportedServices)
				SelectedService = Service[0]
				if isValidRegion(region,SelectedService):
					pass
				else:
					print "${Service[0]} is not present in ${args.region}, defaulting to ${session.region_name}"


			readInput("/%s/%s" % (SelectedService, PresentPath), SupportedCommands)
			print "hello"
			sys.exit()
	except Exception as e:
		raise e


try:
	if __name__ == "__main__":
		if sys.platform not in ['darwin']:
			raise Exception("OS not Supported")
		parser = argparse.ArgumentParser(description='AWS Navigator')
		parser.add_argument('--profile', dest='profile',type=str,default='default',help='AWS Profile')
		parser.add_argument('--region', dest='region',type=str,help='AWS Region Name')
		args = parser.parse_args()
		main(args)
except Exception as e:
	print e