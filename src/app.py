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
    user_trip_details = list()
    for line in request.form.get('logs').split('\r\n'):
        (user_name, trip_time, location) = line.strip().split('\t')
        users_trips.setdefault(user_name, [])
        users_trips[user_name].append(dict(
            time=datetime.strptime(trip_time, '%Y/%m/%d %H:%M:%S'),
            from_city=location.split('-')[0],
            to_city=location.split('-')[1]))
    for user in users_trips:
        users_trips[user].sort(key=lambda i: i['time'])
        start = None
        total_days = 0
        current_trips = []
        for current_trip in users_trips[user]:
            current_trips.append(current_trip)
            if start is None:
                start = current_trip
                continue
            if current_trip['to_city'] == start['from_city']:
                days = cal_trip_days(start['time'], current_trip['time'])
                user_trip_details.append(dict(
                    user=user,
                    start_time=start['time'],
                    end_time=current_trip['time'],
                    trip=' '.join(['%s-%s' % (c['from_city'], c['to_city'])
                                   for c in current_trips]),
                    days=days
                ))

                total_days += days
                start = None
                current_trips = []
            elif current_trip['from_city'] == start['from_city']:
                start = current_trip
                current_trips = [current_trip]
        users_days[user] = total_days
    return render_template(
        'business_trip.html',
        logs=request.form.get('logs'),
        user_days=users_days,
        user_trip_details=user_trip_details
    )

if __name__ == '__main__':
    app.run(debug=True)
