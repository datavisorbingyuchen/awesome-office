#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from flask import Flask, render_template, request

app = Flask(__name__)


def cal_trip_days(start, end):
    days = (end.date() - start.date()).days
    for i in range(days):
        if (start + timedelta(days=i)).weekday() >= 5:
            days -= 1
    return days + 1


@app.route('/business_trip', methods=['GET', 'POST'])
def business_trip():
    if request.method == 'GET':
        return render_template('business_trip.html')
    users_trips = dict()
    users_days = dict()
    for line in request.form.get('logs').split('\r\n'):
        (user_name, trip_time, location) = line.strip().split('\t')
        users_trips.setdefault(user_name, [])
        users_trips[user_name].append(
            (datetime.strptime(trip_time, '%Y/%m/%d %H:%M:%S'),
             location.split('-')[0],
             location.split('-')[1]))
    for user in users_trips:
        users_trips[user].sort(key=lambda i: i[0])
        start = None
        days = 0
        for trip in users_trips[user]:
            if start is None:
                start = trip
                continue
            if trip[2] == start[1]:
                days += cal_trip_days(start[0], trip[0])
                start = None
        users_days[user] = days
    return render_template(
        'business_trip.html',
        logs=request.form.get('logs'),
        user_days=users_days)

if __name__ == '__main__':
    app.run(debug=True)
