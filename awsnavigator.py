#!/usr/bin/python
import boto3
import sys
import re

SupportedServices = ['ec2']
SupportedCommands = ['ls','cd']

def readInput(*args):
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
			#return ""

def main(argv):
	
	while True:
		readInput("enter a dummy value ", SupportedCommands)
		print "hello"
		sys.exit()

try:
	if __name__ == "__main__":
		if sys.platform not in ['darwin']:
			raise Exception("OS not Supported")
		main(sys.argv)
except Exception as e:
	print e