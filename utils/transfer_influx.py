import atexit
import sys
import time
#  Copyright (c) 2020. AV Connect Inc.
from signal import signal, SIGINT
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from influxdb import dataframe_client

INFLUX_EAST = "3.13.34.150"
INFLUX_WEST = "172.31.5.60"


class Transfer(object):
    def __init__(self):
        self.is_running = True

    def transfer_last_20(self, window = "20m"):
        print("Getting last {} of data".format(window))
        client_local = dataframe_client.DataFrameClient(host= INFLUX_EAST, database="telematics")
        response = client_local.query("select * from Grey_Kona WHERE time > now() - {}".format(window))
        # print("local response")
        # print(response["Grey_Kona"][:100])
        # print(response["Grey_Kona"].shape[0])
        source = response["Grey_Kona"]

        client_remote = dataframe_client.DataFrameClient(host=INFLUX_WEST, database="telematics")
        # response2 = client_remote.query("SELECT * FROM Grey_Kona")
        # print("remote response")
        # print(response2["Grey_Kona"][:100])
        print("Writing {} points at {}".format(source.shape[0], str(datetime.now())))

        for i in range(source.shape[0]):
            if i % 60 == 0:
                # print(i)
                client_remote.write_points(source[i:i+60],'Grey_Kona', protocol='line')
        print("Done writing at {}".format(str(datetime.now())))

    def stop_running(self):
        self.is_running = False


if __name__ == "__main__":
    transfer = Transfer()
    transfer.transfer_last_20(sys.argv[1])
    # set up sig listener
    signal(SIGINT, transfer.stop_running)

    # setup jobs1
    scheduler = BackgroundScheduler()
    scheduler.add_job(transfer.transfer_last_20, "interval", seconds=600)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

    # run until stopped
    while transfer.is_running:
        time.sleep(1)
