import os
import csv
import shutil

def make_states(l_path, index = 1):
    with open(os.path.join('..', 'data', l_path), 'r') as read_obj,\
        open(os.path.join('test_data', l_path), 'w') as write_obj:
        csv_reader = csv.reader(read_obj)
        csv_writer = csv.writer(write_obj)
        counter = 0
        for row in csv_reader:
            counter += 1
            if counter == 1 or row[index] == 'Washington':
                csv_writer.writerow(row)

def make_world(l_path, index = 1):
    with open(os.path.join('..', 'data', l_path), 'r') as read_obj,\
        open(os.path.join('test_data', l_path), 'w') as write_obj:
        csv_reader = csv.reader(read_obj)
        csv_writer = csv.writer(write_obj)
        counter = 0
        for row in csv_reader:
            counter += 1
            if counter == 1 or row[index] == 'United_States_of_America':
                csv_writer.writerow(row)


def make_us_all():
    shutil.copy(os.path.join('..', 'data', 'us.csv'), os.path.join('test_data', 'us.csv'))


if __name__ == '__main__':
    make_states('states.csv')
    make_states('states_cases_ranked.csv')
    make_states('states_deaths_ranked.csv')
    make_us_all()
    make_world('world.csv')
    make_world('world_week.csv')

