import sys
sys.path.append('data_call')

import pushingToDB as push

import schedule
import time




schedule.every().day.at("8:00").do(push.updateDBs())
schedule.run_pending()

while True:
    # checks every hour for a pending job
    time.sleep(3600)
    schedule.run_pending()
# set up cron job 1 here
