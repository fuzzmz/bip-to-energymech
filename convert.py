import os
from ConfigParser import SafeConfigParser

def get_log_name(log):
	logs                    = str(log)
	fileName, fileExtension = os.path.splitext(logs) # get file name and extension
	name_start              = fileName.find('#')
	name_end                = fileName.find('.', name_start)
	name                    = fileName[name_start:name_end]
	
	#tests
	print fileName
	print name

	return name

def find_date(log):
	myfile = open(log)
	myfile.seek(0)
	log_text = myfile.read()
	myfile.close()

	log_day = log_text[:2]
	log_month = log_text[3:5]
	log_year = log_text[6:10]

	#tests
	print 'Day is ' + log_day
	print 'Month is ' + log_month
	print 'Year is ' + log_year

	return log_day, log_month, log_year

def write_log(day, month, year, final_log):
	to_write = open(output + name + '_' + year + month + day + '.log', 'w')
	to_write.write(final_log)
	to_write.close()

# read config file
parser = SafeConfigParser()
parser.read('setup.cfg')
log    = parser.get('directories', 'input')
output = parser.get('directories', 'output')

day, month, year = find_date(log)

get_log_name(log)