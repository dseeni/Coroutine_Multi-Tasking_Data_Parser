from src.constants import *
from src.push_pipeline import *
from collections import namedtuple
from contextlib import contextmanager
import csv
from itertools import islice
from datetime import datetime
import dateparser

# cars_header = header_extract(fcars)
# cars = data_reader(fcars, cars_parser, cars_header, cars_class_name)
#
# with cars as c:
#     # for row in c:
#     #     print(row)
#     print('20:', *list(islice(c, 100)), sep='\n')


# for row in cars:
#     print('17:', *list(row), sep='\n')


# file open context manager, coroutine context manager, test within it thats
# the first thing that you need to right

# extract headers as variable
# determine filter names that correspond to these:
#  Car Cheverlot
#  MPG
#  Cylinders
#  Displacement
#  Horsepower
#  Weight
#  Acceleration
#  Model Monte Carlo Landau
#  Origin

# Constants:
# Headers --> NamedTuple
# idx_*headers --> Headers.horsepower etc?
# Input_file --> cars.csv
# Types str in etc
# Output files based on filter names {}


# def infer_data_type(self):
#     for value in self.data_key:
#         if value is None:
#             self.data_key[self.data_key.index(value)] = None
#         elif all(c.isdigit() for c in value):
#             self.data_key[self.data_key.index(value)] = int(value)
#
#         elif value.count('.') == 1:
#             try:
#                 self.data_key[self.data_key.index(value)] = float(value)
#             except ValueError:
#                 self.data_key[self.data_key.index(value)] = str(value)
#
#         else:
#             self.data_key[self.data_key.index(value)] = str(value)
# with pipeline() as pipe:
#         data = data_parser()
#         for row in data:
#                 pipe.send(row)


def infer_data_type():
    data_key = yield
    for value in data_key:
        if value is None:
            data_key[data_key.index(value)] = None
        elif all(c.isdigit() for c in value):
            data_key[data_key.index(value)] = int(value)

        elif value.count('.') == 1:
            try:
                data_key[data_key.index(value)] = float(value)
            except ValueError:
                data_key[data_key.index(value)] = str(value)

        else:
            data_key[data_key.index(value)] = str(value)

# try date first, then literal, then str


print(type(ast.literal_eval('6.2')))

print(type(ast.literal_eval('6.')))
print(type(ast.literal_eval('6')))
try:
    print(type(ast.literal_eval('6-2')))
except ValueError:
    print(str)
try:
    print(type(ast.literal_eval('6A2')))
except Exception:
    print(str)


# def parse_date(value, *, fmt='%Y-%m-%dT%H:%M:%SZ'):
#     return datetime.strptime(value, fmt)


# def date_getter():
#     # for datekey in date_keys:
#     #     try:
#     #         parse_date('12/12/12', fmt=datekey)
#     #     except Exception:
#     #         return str('none')
#     for datekey in date_keys:
#         try:
#             print(datetime.stiptime('12/12/12', datekey))
#         except Exception:
#             print('cant do it')

# print(date_getter())

# Use date parser for dates:
# print(dateparser.parse('12/12/12'))
# print(dateparser.parse('2017-10-07T00:14:42Z'))
# print(type(dateparser.parse('2017-10-07T00:14:42Z')))
# print(datetime.strptime('12/12/2012', '%d/%m/%Y'))
