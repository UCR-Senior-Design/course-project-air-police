import sys
sys.path.append('data_call')

import pushingToDB as push
import datafractionstuff as dfs
import schedule
import time
exit_flag = False

def job():
    push.updateDBs()
def job2():
    dfs.updateDataFraction()
schedule.every(12).hours.do(job2)
schedule.every().day.at("09:00").do(job)
schedule.run_pending()

while not exit_flag:
    # checks every hour for a pending job
    print('running')
    schedule.run_pending()
    print('finished 1')
    time.sleep(3600)

# set up cron job 1 here
