import os
import re
import fnmatch
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
                end_by     = new_line.find('!', start_by)
                by         = new_line[start_by+3:end_by]
                start_mode = new_line[1:].find('[')
                end_mode   = new_line[10:].find(']')
                mode       = new_line[start_mode+2:start_mode+4]
                start_nick = new_line[1:].find('[') + 5
                end_nick   = new_line[10:].find(']') + 10
                nick       = new_line[start_nick:end_nick]
                new_line   = new_line[:11] + "*** " + by + " sets mode: " + mode + ' ' + nick + "\n"
            elif new_line.find('is now known as') != -1:
                new_line = new_line.replace("%^&", "***")
            elif new_line.find('changed topic') != -1:
                start_mask  = new_line.find('!')
                end_mask    = new_line.find(' ', start_mask)
                mask        = new_line[start_mask:end_mask]
                new_line    = new_line.replace(mask, '')
                new_line    = new_line.replace('%^&', '***')
                start_topic = new_line.find('to:')
                topic       = "'" + new_line[start_topic+4:-2] + "'"
                new_line    = new_line[:start_mask]
                new_line    = new_line + ' changes topic to ' + topic + '\n'
            elif new_line.find('Disconnected from server') != -1:
                new_line = 'Disconnected from IRC\n'
            elif new_line.find('Connected to server') != -1:
                new_line = 'Connected to IRC\n'
            elif new_line.find('kicked') != -1:
                new_line         = new_line.replace('%^&', '***')
                new_line         = new_line.replace('had been', 'was')
                start_mask       = new_line.find('!')
                end_mask         = new_line.find(' ', start_mask)
                start_ban_reason = new_line.find('[', start_mask)
                end_ban_reason   = new_line.find(']', start_mask)
                ban_reason       = new_line[start_ban_reason:end_ban_reason]
                new_line         = new_line[:start_mask]
                ban_reason       = ban_reason.replace('[', '(')
                new_line         = new_line + ' ' + ban_reason + ') ' + channel_name +'\n'
            elif new_line.find('Topic for'):
                new_line = ''
            elif new_line.find('Topic set by'):
                new_line = ''
        new_file.write(new_line)
    new_file.close()
    old_file.close()


parser           = SafeConfigParser()
parser.read('setup.cfg')

log              = parser.get('directories', 'input')
output           = parser.get('directories', 'output')

matches = []
for root, dirnames, filenames in os.walk(log):
    for filename in fnmatch.filter(filenames, '*.log'):
        matches.append(os.path.join(root, filename))

for infile in matches:
    day, month, year = find_date(infile)
    channel_name     = get_channel_name(infile)
    
    parse_log(infile, output, channel_name, year, month, day)
    