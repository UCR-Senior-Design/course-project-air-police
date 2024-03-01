import sys
sys.path.append('data_call')

import pushingToDB as push

import schedule
import time




schedule.every().day.at("8:00").do(push.updateDBs())

# set up cron job 1 here
