import influxdb
import numpy as np
from datetime import timedelta

class Range(object):

    def __init__(self, client):
        self.client = client

    def get_days_data(self, vehicle, days_ago, hours_ago, length):
        c = influxdb.DataFrameClient(host='18.237.167.98', port=8086)
        self.client.switch_database("telematics")

        results = self.client.query("select CF_Clu_Odometer,CR_Vcu_DistEmpty_km,CR_Bms_Soc_Pc, CF_Bms_StdCha, CF_Bms_FstCha "
                          "from {} "
                          "where time > now() - {}d - {}h and time < now() - {}d  + {}h ".
                          format(vehicle, days_ago, hours_ago, days_ago, length - hours_ago))
        df = results[vehicle].dropna()

        df_fo = df.loc[(df['CF_Clu_Odometer'] > 1000)]
        # find all spots where battery jumps
        df_fo['soc_plus'] = df_fo['CR_Bms_Soc_Pc'].shift().astype(float) + 2.0
        df_fo['charge_break'] = df_fo['CR_Bms_Soc_Pc'] > df_fo['soc_plus'].shift()
        df_fo['charge_list'] = (df_fo['CF_Bms_StdCha'] > 0) | (df_fo['CF_Bms_FstCha'] > 0)
        return df_fo

    def normalize_days(self, data_frame):
        """
        Return a index of timedeltas from the start of the dataframe
        """
        start_time = data_frame.index[0]
        index = data_frame.index.values
        for i in index:
            i = i - start_time
        return index

    def get_delta_soc(self, df):
        df['res_soc'] = df['CR_Bms_Soc_Pc'] - df['CR_Bms_Soc_Pc'].shift()
        df.res_soc = df.res_soc.fillna(0)
        df['res_fil_soc'] = [0 if df.charge_list[i] else df.res_soc[i] for i in df.res_soc.index]
        print("data size {}".format(str(len(df.res_soc))))
        return df.res_fil_soc

    def get_kmmpt(self, df_fo, km):
        import numpy as np

        def get_forward_kmppct(df, start_index, km):
            index_end = df['CF_Clu_Odometer'].index[-1]
            current_index = start_index
            current_time_index = df['CF_Clu_Odometer'].index[start_index]
            km_done = df['CF_Clu_Odometer'][current_time_index] + km
            charge_used = 0
            while current_time_index < index_end:
                current_time = df['res_fil_soc'].index[current_index]
                charge_used += df['res_fil_soc'][current_time]
                if df['CF_Clu_Odometer'][current_time] >= km_done:
                    break
                current_index += 1
                current_time_index = df['CF_Clu_Odometer'].index[current_index]

            return charge_used, current_index
        km_tag = 'kmppct_' + str(km)
        df_fo[km_tag] = np.nan
        for index in range(0, len(df_fo.res_soc), 500):
            if index % 500 == 0:
                print(index)
            ts = df_fo.res_soc.index[index]
            charge_used, current_index = get_forward_kmppct(df_fo, index, km)
            if charge_used != 0:
                df_fo[km_tag][current_index] = -1 * km / charge_used

        return df_fo[km_tag]

    def get_vehicle_range_estimate(self, df):
        df['rng_est'] = np.nan
        for index in range(0, len(df.res_soc), 10):
            time_index = df.res_soc.index[index]
            df.rng_est[time_index] = \
                df.CR_Vcu_DistEmpty_km[time_index] / df.CR_Bms_Soc_Pc[time_index]

        return df.rng_est