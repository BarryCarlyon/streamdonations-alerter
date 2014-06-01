from distutils.core import setup
import py2exe

setup(
	console = ['donations.py'],
	data_files = ['settings.ini','README.txt','mostRecentDonator.txt','topDonator.txt','donatorList.txt','sound.wav','cacert.pem'],
	options = {
		"py2exe":{
			"includes": ["socketIO_client"]
		}
	}
)