import os
import glob
from ConfigParser import SafeConfigParser

def get_channel_name(log):
	logs                    = str(log)
	fileName, fileExtension = os.path.splitext(logs) # get file name and extension
	name_start              = fileName.find('#')
	name_end                = fileName.find('.', name_start)
	name                    = fileName[name_start:name_end]
	
	#tests
	print 'Log file name is ' + fileName
	print 'Channel name is '  + name

	return name

def find_date(log):
	myfile    = open(log)
	myfile.seek(0)
	log_text  = myfile.read()
	myfile.close()
	
	log_day   = log_text[:2]
	log_month = log_text[3:5]
	log_year  = log_text[6:10]
	
	#tests
	print 'Day is '   + log_day
	print 'Month is ' + log_month
	print 'Year is '  + log_year

	return log_day, log_month, log_year

def parse_log(log, output, channel_name, year, month, day):
	new_file = open(output + channel_name + '_' + year + month + day + '.log','w')
	old_file = open(log)
	for line in old_file:
		new_file.write(line[11:])
	new_file.close()
	old_file.close()

# read config file
parser           = SafeConfigParser()
parser.read('setup.cfg')

log              = parser.get('directories', 'input')
output           = parser.get('directories', 'output')

for infile in glob.glob(os.path.join(log, '*.log')):
	#tests
	print "Current file is: " + infile

	day, month, year = find_date(infile)
	channel_name     = get_channel_name(infile)
	
	parse_log(infile, output, channel_name, year, month, day)