#  Copyright (c) 2020. AV Connect Inc.
from datetime import datetime
from functools import reduce

import dateutil.parser
import influxdb
import pytz


class Telematics(object):
    """
    Manage an influx db connection
    """
    def __init__(self, config):
        self.config = config
        print(self.config['INFLUX_DB'])
        self.influx = influxdb.client.InfluxDBClient(
                self.config['INFLUX_HOST'],
                self.config['INFLUX_PORT'],
                database=self.config['INFLUX_DB'])
        self.influx_pandas = influxdb.dataframe_client.DataFrameClient(
                self.config['INFLUX_HOST'],
                self.config['INFLUX_PORT'],
                database=self.config['INFLUX_DB'])

    def get_vehicles(self):
        """
        :return: list of all the vehicles for which we have data
        """
        result = self.influx.get_list_measurements()
        return [l['name'] for l in result]

    def get_field_keys(self, measurement):
        """
        :param measurement: The vehicle we're interested in.
        :return: list of all the data fields that are recorded for this vehicle.
        """
        result = self.influx.query("show field keys from {}".format(measurement))
        return [l['fieldKey'] for l in result[measurement]]

    def get_latest_from(self, measurement, keys):
        """
        :param measurement:
        :param keys:
        :return: Time series dict of the latest values from the given keys on the given car.
        """
        key_string = reduce(lambda p,c : p + "," + c, keys)
        query = "SELECT {} FROM {} GROUP BY * ORDER BY DESC LIMIT 1".format(key_string, measurement)
        print(query)
        result = self.influx.query(query)
        return [value for value in result[measurement]]

    def get_data(self, measurement, keys, start_time, end_time, use_pandas=False):
        """
        :param measurement:
        :param keys: comma separated list of all keys we want to query
        :param start_time: utc date time
        :param end_time: utc date time
        :param is_pandas: if true data is returned as a pandas dataframe
        :return: measurement data in json format
        """
        key_string = reduce(lambda p, c: p + "," + c, keys)
        st = self._date_time_to_query_string(start_time)
        et = self._date_time_to_query_string(end_time)
        query = "SELECT {} FROM {} WHERE time > '{}' AND time <= '{}'".format(key_string, measurement, st, et)
        print(query)
        if use_pandas:
            result = self.influx_pandas.query(query)
        else:
            result = self.influx.query(query)
        return result

    def write_data(self, vehicle, json_data):
        """
        Json data does not include timestamp.
        :param vehicle:
        :param json_data:
        :return:
        """
        data = ""
        for message in json_data['messages']:
            ts = message['time']
            print("time: " + str(ts))
            for key in message.keys():
                if key != 'time' and key !='vehicle_name':
                    data += "{} {}={} {}\n".format(vehicle, key, message[key], ts)
        print(data)
        self.influx.write_points([data], protocol='line')

    def write_array_data(self, message):
        """
        Data in form {"vehicle_name":<name>, "data":{"<key1>":[[<ts1>,<data1>],[<ts2>,<data2>], ...}
        :return:
        """
        vehicle_name = message["vehicle_name"]
        data = ""
        for message in message['messages']:
            tokens = message.split(",")
            data += "{} {}={} {}\n".format(vehicle_name, tokens[0], tokens[2], tokens[1])
        self.influx.write_points([data], protocol='line')

    def get_todays_data(self, measurement, keys, timezone, use_pandas=False):
        """
        Get all data from the vehicle from 12AM until now in the timezone given
        :param timezone:
        :return:
        """
        current = datetime.now(tz=timezone)
        start = current.replace(minute=0, hour=0, second=0, microsecond=0)
        start_utc = start.astimezone(pytz.UTC)
        end_utc = current.astimezone(pytz.UTC)
        print("start/end {} {}".format(start_utc, end_utc))
        return self.get_data(measurement, keys, start_utc, end_utc, use_pandas)


    def _date_time_to_query_string(self, timestamp):
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")

    def get_all_data(self, measurement, keys):
        key_string = reduce(lambda p, c: p + "," + c, keys)
        query = "SELECT {} FROM {}".format(key_string, measurement)
        result = self.influx.query(query)
        return [value for value in result[measurement]]

    @classmethod
    def telematics_to_datetime(cls, datetime_string):
        """ Return a UTC, tz aware datetime of the string
        """
        return dateutil.parser.parse(datetime_string).astimezone(pytz.utc)

    @classmethod
    def telematics_to_sec(cls, datetime_string):
        """ Return seconds since the UNIX epoch """
        dt = cls.telematics_to_datetime(datetime_string)
        return int((dt-datetime(1970,1,1,tzinfo=pytz.utc)).total_seconds())

    @classmethod
    def dt_to_sec(cls, dt):
        return int((dt - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds())

