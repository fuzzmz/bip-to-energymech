import os
import glob
import re
from ConfigParser import SafeConfigParser


talk_mask    = re.compile('\!.*?\:')
connect_mask = re.compile('\!.*?\has')
quit_info    = re.compile('\quit.*?\]')
find_nick    = re.compile('\<* .*?\!')
time_mask    = re.compile('([0-1]\d|2[0-3]):([0-5]\d):([0-5]\d)')


def get_channel_name(log):
    logs                    = str(log)
    fileName, fileExtension = os.path.splitext(logs) # get file name and extension
    name_start              = fileName.find('#')
    name_end                = fileName.find('.', name_start)
    name                    = fileName[name_start:name_end]

    return name

def find_date(log):
    myfile    = open(log)
    myfile.seek(0)
    log_text  = myfile.read()
    myfile.close()
    
    log_day   = log_text[:2]
    log_month = log_text[3:5]
    log_year  = log_text[6:10]

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
            if new_line.find('<*') != -1:
                nick_find          = re.search(find_nick, new_line)
                nick               = nick_find.group(0)
                nick               = nick[2:-1]
                mask               = new_line.find('!')
                mask_message_start = new_line[mask:]
                message_find       = mask_message_start.find(' ')
                message            = mask_message_start[message_find+1:]
                new_line           = new_line[:11] + nick + " " + message
            else:
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
            elif new_line.find('mode') != -1:
                start_by   = new_line.find('by ')
                end_by     = new_line.find('!')
                by         = new_line[start_by+3:end_by]
                start_mode = new_line[1:].find('[')
                end_mode   = new_line[10:].find(']')
                mode       = new_line[start_mode+2:start_mode+5]
                start_nick = new_line[1:].find('[') + 5
                end_nick   = new_line[10:].find(']') + 10
                nick       = new_line[start_nick:end_nick]
                new_line   = new_line[:11] + "*** " + by + " sets mode: " + mode + nick + "\n"
            #TODO write case for topic information and owner-user disconnect/connect
            elif new_line.find('is now known as') != -1:
                new_line = new_line.replace("%^&", "***")
        new_file.write(new_line)
    new_file.close()
    old_file.close()


# read config file
parser           = SafeConfigParser()
parser.read('setup.cfg')

log              = parser.get('directories', 'input')
output           = parser.get('directories', 'output')

for infile in glob.glob(os.path.join(log, '*.log')):
    day, month, year = find_date(infile)
    channel_name     = get_channel_name(infile)
    
    parse_log(infile, output, channel_name, year, month, day)
    