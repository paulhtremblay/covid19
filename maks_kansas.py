import csv
import datetime
with open('masks_kansas.csv', 'r') as read_obj:
    for line in read_obj:
        fields = line.split(',')
        if len(fields) < 2:
            continue
        date = datetime.datetime.strptime(fields[1].strip(), '%m/%d/%Y')
        print('{f1},{f2}'.format(f1 = fields[0], 
            f2 = date.strftime('%Y-%m-%d')))

