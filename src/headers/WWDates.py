## ###############################################################
## LOAD MODULES
## ###############################################################
import datetime


## ###############################################################
## HELPER FUNCTIONS TO WORK WITH DATES
## ###############################################################
def castDate2String(date):
  str_year  = str(date.year ).zfill(4)
  str_month = str(date.month).zfill(2)
  str_day   = str(date.day  ).zfill(2)
  return f"{str_year}-{str_month}-{str_day}"

def castString2Date(str_date):
  return datetime.datetime.strptime(str_date, "%Y-%m-%d").date()

def getDateToday():
  return datetime.datetime.now()

def getDateNDaysAgo(num_days):
  date_today = datetime.datetime.now()
  date_delta = datetime.timedelta(days=int(num_days))
  date_ago  = date_today - date_delta
  return date_ago


## END OF HEADER FILE