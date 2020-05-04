import datetime
import os
with open(os.path.join('html_dir', 'index.html'), 'r') as read_obj:
    s = ''.join(read_obj.readlines())
with open(os.path.join('html_temp', 'index.html'), 'w') as write_obj:
    s = s.format(date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    write_obj.write(s)

with open(os.path.join('html_dir', '404.html'), 'r') as read_obj:
    s = ''.join(read_obj.readlines())

with open(os.path.join('html_temp', '404.html'), 'w') as write_obj:
    s = s.format(date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    write_obj.write(s)
