#!/usr/bin/env python3

# A Gitter bot to automatically post message(s) on the SecureDrop room. It can post
# message(s) on any day of the week, at any specified time value(s). The behaviour
# of the bot can be configured in 'data.yml'. It can be used in any other Gitter
# room as well.

import calendar
import datetime
import functools
import json
import requests
import schedule
import time
import traceback
import yaml

# Room id of "https://gitter.im/freedomofpress/securedrop".
securedrop_room_id = '53bb302d107e137846ba5db7'

target_url = 'https://api.gitter.im/v1/rooms/' + securedrop_room_id + '/chatMessages'


# A function which returns a decorator function for handling exceptions that happen
# during job execution.
def catch_exceptions(cancel_on_failure=False):
    def decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                print(traceback.format_exc())
                if cancel_on_failure:
                    return schedule.CancelJob
        return wrapper
    return decorator

# Read the API Token from external file.
def get_api_token():

    with open("auth.yml", 'r') as auth_ymlfile:
        try:
            c = yaml.load(auth_ymlfile)
        except yaml.YAMLError as exc_a:
            print(exc_a)
    
    api_token = c['apitoken']
    return api_token


# Read the message to be posted along with the day(s) and time value(s)
# from 'data.yml'. Returns a list of all tasks (a task is a particular
# message to be posted), in which each task itself is a list of 3 items.
def get_data():

    task = []
    list_of_tasks = []

    with open("data.yml", 'r') as data_ymlfile:
        try:
            cfg = yaml.load(data_ymlfile)
        except yaml.YAMLError as exc_d:
            print(exc_d)

    for section in cfg:
        task.extend([cfg[section]['message'],
                sorted(cfg[section]['day']),
                sorted(cfg[section]['time'])])
        new_task = list(task)
        list_of_tasks.append(new_task)
        task.clear()
    
    return list_of_tasks


# The job of the bot, making a POST request with the headers and data
@catch_exceptions(cancel_on_failure=True)
def job(msg):

    api_token = get_api_token()
    headers = {'Content-Type': 'application/json',
           'Accept': 'application/json',
           'Authorization': 'Bearer {0}'.format(api_token)}
    data = {'text': msg}

    print('On {0} at {1}:{2}'.format(datetime.datetime.now().date(),
                                str(datetime.datetime.now().time().hour).zfill(2),
                                str(datetime.datetime.now().time().minute).zfill(2)))
    response = requests.post(target_url, headers=headers, json=data)
    
    if response.status_code >= 500:
        print('[{0}] Server Error.'.format(response.status_code))
    elif response.status_code == 404:
        print('[{0}] URL not found: [{1}]'.format(response.status_code, target_url))
    elif response.status_code == 401:
        print('[{0}] Authentication Failed.'.format(response.status_code))
    elif response.status_code >= 400:
        print('[{0}] Bad Request.'.format(response.status_code))
    elif response.status_code >= 300:
        print('[{0}] Unexpected redirect.'.format(response.status_code))
    elif response.status_code == 200:
        print('[{0}] The request succeeded.\n'.format(response.status_code))
        print('Posted the following message: \n{0}\n'.format(msg))
        print('Received the following response: \n{0}\n\n\n'.format(response.json()))
    else:
        print('Unexpected Error: [HTTP {0}]: Content: {1}'.format(response.status_code,
                                                                  response.content))


def main():

    # Make a list of all days. Week starts from Monday, at index 0 of the list
    all_days = list(calendar.day_name)

    list_of_tasks = get_data()

    for task in list_of_tasks:
        for day_of_week in task[1]:
            for this_time in task[2]:
                getattr(schedule.every(),
                        str(all_days[day_of_week]).lower()).at(this_time).do(job, msg = task[0])

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()