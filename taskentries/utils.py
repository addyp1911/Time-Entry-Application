import datetime, pytz

def fetch_current_time():
    tz_asia = pytz.timezone('Asia/Kolkata')
    current_time = tz_asia.fromutc(datetime.datetime.utcnow()).replace(tzinfo=pytz.UTC).strftime('%Y-%m-%dT%H:%M:%S %z')
    current_time_obj = datetime.datetime.strptime(current_time, '%Y-%m-%dT%H:%M:%S %z')
    return current_time_obj


def convert_time_format(current_time_obj, time_entry):
    logged_time = current_time_obj - time_entry.task_start
    duration = logged_time.total_seconds()
    hours = int(duration // 3600) 
    hours = '00' if not hours else hours
    minutes = int((duration % 3600) // 60)
    seconds = int(duration % 60)
    time_tracked = '{}:{}:{}'.format(hours, minutes, seconds)
    return time_tracked