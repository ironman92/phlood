import argparse



# Version Check
from platform import python_version
if python_version()[0] != '3':
    print("Must be run with python 3")
    exit()



# Parse Command Line Arguments
parser = argparse.ArgumentParser(description='''
	CNS 210 Class Project
	PHlood 2020-05-09
	CIS 210 2020
	Morgan Matchette & Ryan Stark''')
parser.add_argument('--logfile',
                    help='File to log to',
                    action='store',
                    dest='logfile',
                    type=str,
                    required=False,
                    metavar='FILE')
argument = parser.parse_args()



# File existance sanity check
if os.path.isfile(argument.logfile):
    overwrite = input("File exists. Overwrite (y/N)? ")
    if len(overwrite) <= 0 or overwrite[0] not in ['Y', 'y']:
        exit()
