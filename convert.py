import os
import glob
import re
from ConfigParser import SafeConfigParser

talk_mask    = re.compile('\!.*?\:')
connect_mask = re.compile('\!.*?\has')
quit_info    = re.compile('\quit.*?\]')
time_mask    = re.compile('([0-1]\d|2[0-3]):([0-5]\d):([0-5]\d)')

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
		new_line = line[11:]
		time     = re.search(time_mask, new_line)
		new_line = re.sub(time_mask, '[' + time.group(0) + ']', new_line)
		new_line = new_line.replace("< ", "<", 1)
		new_line = new_line.replace("-!-", "%^&")
		if new_line.find('<') != -1:
			new_line = re.sub(talk_mask, '>', new_line)
		elif new_line.find('%^&') != -1:
			if new_line.find('quit') != -1:
				new_line     = new_line.replace("%^&", "*** Quits:")
				m            = re.search(connect_mask, new_line)
				mask         = ' (' + m.group(0)[1:-4] + ')'
				new_line     = re.sub(connect_mask, mask, new_line)
				q            = re.search(quit_info, new_line)
				quit_message = '(' + q.group(0)[6:-1] +')'
				new_line     = re.sub(quit_info, quit_message, new_line)
			elif new_line.find('join') != -1:
				new_line = new_line.replace("%^&", "*** Joins:")
				m        = re.search(connect_mask, new_line)
				mask     = ' (' + m.group(0)[1:-4] + ')'
				new_line = re.sub(connect_mask, mask, new_line)
				end      = new_line.find('joined')
				new_line = new_line[:end-1] + '\n'
		new_file.write(new_line)
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