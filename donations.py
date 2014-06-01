from decimal import *
from socketIO_client import SocketIO
import ConfigParser
import json
import time
import os
import urllib2
import winsound

os.environ['REQUESTS_CA_BUNDLE'] = 'cacert.pem'

topDonorAmount = float(0)
recentDonations = []
donationsPolled = False
version = "2.0"

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
							localFile = open('topDonator.txt', 'w')
							localFile.write(" %s " % topDonationFormatted.encode("utf-8", errors='ignore'))
							localFile.close()
							print "Updated top donation to: %s" % topDonationFormatted.encode("utf-8", errors='ignore')
						else:
							print "Top donation lower than minimum. Setting top donation to nobody."
							localFile = open('topDonator.txt', 'w')
							localFile.write(" ")
							localFile.close()
					except IndexError:
						print "No top donation. Setting top donation to nobody."
						localFile = open('topDonator.txt', 'w')
						localFile.write(" ")
						localFile.close()
				else:
					print "Setting top donation to nobody."
					localFile = open('topDonator.txt', 'w')
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
						localFile = open('donatorList.txt', 'w')
						localFile.write(" %s " % donationList.encode("utf-8", errors='ignore'))
						localFile.close()
						print "Updated donation list to: %s" % donationList.encode("utf-8", errors='ignore')
					except:
						print "No recent donations. Donation list is empty."
						localFile = open('donatorList.txt', 'w')
						localFile.write(" ")
						localFile.close()
				else:
					print "Setting donation list to empty."
					localFile = open('donatorList.txt', 'w')
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
							localFile = open('mostRecentDonator.txt', 'w')
							localFile.write(" %s " % donationFormatted.encode("utf-8", errors='ignore'))
							localFile.close()
							print "Updated most recent donator to: %s" % donationFormatted.encode("utf-8", errors='ignore')
						else:
							print "Most recent donation lower than minimum. Setting most recent donation to nobody."
							localFile = open('mostRecentDonator.txt', 'w')
							localFile.write(" ")
							localFile.close()
					except:
						print "No most recent donation. Setting most recent donation to nobody."
						localFile = open('mostRecentDonator.txt', 'w')
						localFile.write(" ")
						localFile.close()
				else:
					print "Setting most recent donation to nobody."
					localFile = open('mostRecentDonator.txt', 'w')
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
				localFile = open('topDonator.txt', 'w')
				localFile.write(" %s " % topDonationFormatted.encode("utf-8", errors='ignore'))
				localFile.close()
		else:
			print 'We have a new donation!'

		print("--->  %s  <---" % consoleDonationFormatted.encode("utf-8", errors='ignore'))

		if float(donation["amount"]) >= fileMinimum:
			localFile = open('mostRecentDonator.txt', 'w')
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
			localFile = open('donatorList.txt', 'w')
			localFile.write(" %s " % donationList.encode("utf-8", errors='ignore'))
			localFile.close()

		if float(donation["amount"]) >= soundMinimum:
			if playWAVonDonation == True:
				if isTopDonation == True:
					playWAV("top")
				else:
					playWAV("regular")

	def playWAV(type):
		if type == "top":
			winsound.PlaySound(topDonationWAV, winsound.SND_FILENAME)
		else:
			winsound.PlaySound(donationWAV, winsound.SND_FILENAME)

	Config = ConfigParser.ConfigParser()
	Config.read("settings.ini")
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
	socketIO = SocketIO('https://www.streamdonations.net', 443)
	socketIO.on('login', login)
	socketIO.on('authenticated', authenticated)
	socketIO.on('authentication failed', authenticationFailed)
	socketIO.on('new donation', newDonation)
	socketIO.wait()

def main():
	try:
		getConnected()
	except Exception, e:
		if ("No section" in str(e)):
			print "Your settings.ini file is missing or corrupted. Fix the issue and restart the program/wait 30 seconds."
			time.sleep(30)
		elif ("No option" in str(e)):
			print e
			print "In other words, the option is missing/malformed in your settings.ini file. Fix the issue and restart the program/wait 30 seconds."
			time.sleep(30)
		elif ("HTTP Error" in str(e)):
			print e
			print "It looks like my server is having some issues. Retrying in 30 seconds.."
			time.sleep(30)
		else:
			print e
			print "Interesting.. Trying again in 30 seconds.."
			time.sleep(30)

if __name__ == "__main__":
	print "Donation Tracker Alerter v%s loaded" % version
	while True:
		main()