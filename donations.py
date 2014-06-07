from decimal import *
from socketIO_client import SocketIO
import ConfigParser
import json
import time
import sys, os
import urllib2
import winsound

import logging
logging.basicConfig(level=logging.DEBUG)

topDonorAmount = float(0)
recentDonations = []
donationsPolled = False
version = "3.0"

internal_working_dir = os.getcwd()

os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(os.path.dirname(__file__), "cacert.pem")
cacert_location = False

def str2bool(v):
	return v.lower() in ("yes", "true", "t", "1")

def getConnected():

	global topDonorAmount
	global recentDonations
	global donationsPolled

	def login():
		emitData = json.dumps({'channel': channel, 'key': key})
		socketIO.emit('auth', emitData)

	def authenticated():

		global topDonorAmount
		global recentDonations
		global donationsPolled

		print ' '
		print 'Logged into the Donation Tracker as %s' % channel
		print ' '
		
		if donationsPolled == False:
			print 'Polling donation server..'
			u = urllib2.urlopen('https://www.streamdonations.net/api/poll?channel=%s&key=%s' % (channel, key))
			currentDonations = u.read()
			currentDonations = json.loads(currentDonations)
			if currentDonations["status"] == "success":
				topDonor = currentDonations["top"]
				mostRecentDonor = currentDonations["mostRecent"]
				if dailyTopDonation == False:
					try:
						topDonor = topDonor[0]
						if float(topDonor["amount"]) >= fileMinimum:
							topDonorAmount = float(topDonor["amount"])
							if topDonor["note"] == None:
								topDonor["note"] = "No Message"
							if topDonor["twitchUsername"] == None:
								topDonor["twitchUsername"] = "Anonymous"
							topDonationFormatted = topDonationFormatting.replace("{amount}",topDonor["amount"]).replace("{note}",topDonor["note"]).replace("{username}",topDonor["twitchUsername"]).replace("{processor}",topDonor["processor"]).replace("{currencySymbol}",topDonor["currencySymbol"])
							localFile = open(resourcePath('topDonator.txt', user=True), 'w')
							localFile.write(" %s " % topDonationFormatted.encode("utf-8", errors='ignore'))
							localFile.close()
							print "Updated top donation to: %s" % topDonationFormatted.encode("utf-8", errors='ignore')
						else:
							print "Top donation lower than minimum. Setting top donation to nobody."
							localFile = open(resourcePath('topDonator.txt', user=True), 'w')
							localFile.write(" ")
							localFile.close()
					except IndexError:
						print "No top donation. Setting top donation to nobody."
						localFile = open(resourcePath('topDonator.txt', user=True), 'w')
						localFile.write(" ")
						localFile.close()
				else:
					print "Setting top donation to nobody."
					localFile = open(resourcePath('topDonator.txt', user=True), 'w')
					localFile.write(" ")
					localFile.close()

				if dailyDonationList == False:
					try:
						donationList = ""
						i = 0
						for donor in mostRecentDonor:
							i += 1
							if i <= donationListAmount:
								if float(donor["amount"]) >= fileMinimum:
									if donor["note"] == None:
										donor["note"] = "No Message"
									if donor["twitchUsername"] == None:
										donor["twitchUsername"] = "Anonymous"
									if i == 1:
										donationList += donationListFormatting.replace("{amount}",donor["amount"]).replace("{note}",donor["note"]).replace("{username}",donor["twitchUsername"]).replace("{processor}",donor["processor"]).replace("{currencySymbol}",donor["currencySymbol"])
									else:
										donationList += ", "+donationListFormatting.replace("{amount}",donor["amount"]).replace("{note}",donor["note"]).replace("{username}",donor["twitchUsername"]).replace("{processor}",donor["processor"]).replace("{currencySymbol}",donor["currencySymbol"])
									recentDonations.append(donationListFormatting.replace("{amount}",donor["amount"]).replace("{note}",donor["note"]).replace("{username}",donor["twitchUsername"]).replace("{processor}",donor["processor"]).replace("{currencySymbol}",donor["currencySymbol"]))
						localFile = open(resourcePath('donatorList.txt', user=True), 'w')
						localFile.write(" %s " % donationList.encode("utf-8", errors='ignore'))
						localFile.close()
						print "Updated donation list to: %s" % donationList.encode("utf-8", errors='ignore')
					except:
						print "No recent donations. Donation list is empty."
						localFile = open(resourcePath('donatorList.txt', user=True), 'w')
						localFile.write(" ")
						localFile.close()
				else:
					print "Setting donation list to empty."
					localFile = open(resourcePath('donatorList.txt', user=True), 'w')
					localFile.write(" ")
					localFile.close()

				if dailyRecentDonation == False:
					try:
						mostRecentDonor = mostRecentDonor[0]
						if float(mostRecentDonor["amount"]) >= fileMinimum:
							if mostRecentDonor["note"] == None:
								mostRecentDonor["note"] = "No Message"
							if mostRecentDonor["twitchUsername"] == None:
								mostRecentDonor["twitchUsername"] = "Anonymous"
							donationFormatted = donationFormatting.replace("{amount}",mostRecentDonor["amount"]).replace("{note}",mostRecentDonor["note"]).replace("{username}",mostRecentDonor["twitchUsername"]).replace("{processor}",mostRecentDonor["processor"]).replace("{currencySymbol}",mostRecentDonor["currencySymbol"])
							localFile = open(resourcePath('mostRecentDonator.txt', user=True), 'w')
							localFile.write(" %s " % donationFormatted.encode("utf-8", errors='ignore'))
							localFile.close()
							print "Updated most recent donator to: %s" % donationFormatted.encode("utf-8", errors='ignore')
						else:
							print "Most recent donation lower than minimum. Setting most recent donation to nobody."
							localFile = open(resourcePath('mostRecentDonator.txt', user=True), 'w')
							localFile.write(" ")
							localFile.close()
					except:
						print "No most recent donation. Setting most recent donation to nobody."
						localFile = open(resourcePath('mostRecentDonator.txt', user=True), 'w')
						localFile.write(" ")
						localFile.close()
				else:
					print "Setting most recent donation to nobody."
					localFile = open(resourcePath('mostRecentDonator.txt', user=True), 'w')
					localFile.write(" ")
					localFile.close()

				print ' '

			print 'Current Top Donation set to: %s' % topDonorAmount
			donationsPolled = True
		print 'Incoming donations will now be processed'

	def authenticationFailed():
		print 'Authentication Failed for %s' % channel

	def newDonation(donation):

		global topDonorAmount
		global recentDonations

		donationFormatted = donationFormatting.replace("{amount}",donation["amount"]).replace("{note}",donation["note"]).replace("{username}",donation["twitchUsername"]).replace("{processor}",donation["processor"]).replace("{currencySymbol}",donation["currencySymbol"])
		donationListFormatted = donationListFormatting.replace("{amount}",donation["amount"]).replace("{note}",donation["note"]).replace("{username}",donation["twitchUsername"]).replace("{processor}",donation["processor"]).replace("{currencySymbol}",donation["currencySymbol"])
		topDonationFormatted = topDonationFormatting.replace("{amount}",donation["amount"]).replace("{note}",donation["note"]).replace("{username}",donation["twitchUsername"]).replace("{processor}",donation["processor"]).replace("{currencySymbol}",donation["currencySymbol"])
		consoleDonationFormatted = consoleDonationFormatting.replace("{amount}",donation["amount"]).replace("{note}",donation["note"]).replace("{username}",donation["twitchUsername"]).replace("{processor}",donation["processor"]).replace("{currencySymbol}",donation["currencySymbol"])

		print ' '

		if float(donation["amount"]) > topDonorAmount:
			isTopDonation = True
		else:
			isTopDonation = False

		if isTopDonation == True:
			topDonorAmount = float(donation["amount"])
			print 'We have a new TOP donation!!'
			if float(donation["amount"]) >= fileMinimum:
				localFile = open(resourcePath('topDonator.txt', user=True), 'w')
				localFile.write(" %s " % topDonationFormatted.encode("utf-8", errors='ignore'))
				localFile.close()
		else:
			print 'We have a new donation!'

		print("--->  %s  <---" % consoleDonationFormatted.encode("utf-8", errors='ignore'))

		if float(donation["amount"]) >= fileMinimum:
			localFile = open(resourcePath('mostRecentDonator.txt', user=True), 'w')
			localFile.write(" %s " % donationFormatted.encode("utf-8", errors='ignore'))
			localFile.close()

			if len(recentDonations) == donationListAmount:
				recentDonations.pop()

			recentDonations.insert(0, donationListFormatted)

			donationList = ""
			i = 0
			for donor in recentDonations:
				i += 1
				if i == 1:
					donationList += donor
				else:
					donationList += ", "+donor
			localFile = open(resourcePath('donatorList.txt', user=True), 'w')
			localFile.write(" %s " % donationList.encode("utf-8", errors='ignore'))
			localFile.close()

		if float(donation["amount"]) >= soundMinimum:
			if playWAVonDonation == True:
				if isTopDonation == True:
					playWAV("top")
				else:
					playWAV("regular")

	def playWAV(donationType):
		if donationType == "top":
			winsound.PlaySound(resourcePath(topDonationWAV, user=True), winsound.SND_FILENAME)
		else:
			winsound.PlaySound(resourcePath(donationWAV, user=True), winsound.SND_FILENAME)

	Config = ConfigParser.ConfigParser()
	Config.read(resourcePath('settings.ini', user=True))
	channel = Config.get("Donation Tracker Config", 'Channel').lower()
	key = Config.get("Donation Tracker Config", 'API-Key')
	dailyTopDonation = str2bool(Config.get("Donation Tracker Config", 'DailyTopDonation'))
	dailyRecentDonation = str2bool(Config.get("Donation Tracker Config", 'DailyRecentDonation'))
	dailyDonationList = str2bool(Config.get("Donation Tracker Config", 'DailyDonationList'))
	playWAVonDonation = str2bool(Config.get("Donation Tracker Config", 'PlayWAV'))
	if playWAVonDonation == True:
		donationWAV = Config.get("Donation Tracker Config", 'DonationWAV')
		topDonationWAV = Config.get("Donation Tracker Config", 'TopDonationWAV')
	donationFormatting = Config.get("Donation Tracker Config", 'DonationFormatting').encode("utf-8", errors='ignore')
	donationListFormatting = Config.get("Donation Tracker Config", 'DonationListFormatting').encode("utf-8", errors='ignore')
	topDonationFormatting = Config.get("Donation Tracker Config", 'TopDonationFormatting').encode("utf-8", errors='ignore')
	consoleDonationFormatting = Config.get("Donation Tracker Config", 'ConsoleFormatting').encode("utf-8", errors='ignore')
	donationListAmount = int(Config.get("Donation Tracker Config", 'DonationListAmount'))
	soundMinimum = float(Config.get("Donation Tracker Config", 'SoundMinimum'))
	fileMinimum = float(Config.get("Donation Tracker Config", 'FileMinimum'))
	if not channel:
		raise Exception('Channel is blank in config')
	if not key:
		raise Exception('API-Key is blank in config')
	socketIO = SocketIO('https://www.streamdonations.net') # , 443, verify=cacert_location
	socketIO.on('login', login)
	socketIO.on('authenticated', authenticated)
	socketIO.on('authentication failed', authenticationFailed)
	socketIO.on('new donation', newDonation)
	socketIO.wait()

def start_tracking(internal_resource_path):
	global internal_working_dir
	global cacert_location
	
	internal_working_dir = internal_resource_path
	
	#os.environ['REQUESTS_CA_BUNDLE'] = resourcePath('cacert.pem')
	cacert_location = os.environ['REQUESTS_CA_BUNDLE']
	
	print "Donation Tracker v%s" % version
	print ''
	
	while True:
		try:
			getConnected()
		except Exception, e:
			if ("No section" in str(e)):
				print "Your settings.ini file is missing or corrupted. Please exit and update the configuration."
				time.sleep(30)
			elif ("No option" in str(e)):
				print e
				print "In other words, the option is missing/malformed in your configuration. Please exit and update the configuration."
				time.sleep(30)
			elif ("HTTP Error" in str(e)):
				print e
				print "It looks like my server is having some issues. Please exit and update the configuration."
				time.sleep(30)
			else:
				print e
				print "Interesting.. Please exit and update the configuration."
				time.sleep(30)

def resourcePath(relative_path = '', user = False):
	base_dir = ''
	
	if getattr(sys, 'frozen', False):
		# running in a PyInstaller bundle
		if (user == False):
			# bundle dir
			base_dir = internal_working_dir
		else:
			# user access dir
			base_dir = os.path.dirname(sys.executable)
	else:
		# running in normal Python environment
		base_dir = os.path.dirname(__file__)
	
	return os.path.join(base_dir, relative_path)

if __name__ == "__main__":
	start_tracking(os.path.dirname(__file__))
