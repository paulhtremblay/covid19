import os
from configparser import ConfigParser
d = os.path.dirname(__file__)
path = os.path.join(d, 'config.ini')
parser = ConfigParser()
parser.read(path)
values = dict(parser.items('default'))
