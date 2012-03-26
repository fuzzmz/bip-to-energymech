import os
from ConfigParser import SafeConfigParser

# read config file
parser = SafeConfigParser()
parser.read('setup.cfg')
log    = parser.get('directories', 'input')
output = parser.get('directories', 'output')