#  Copyright (c) 2020. AV Connect Inc.
import redis


class RedisState(object):
    """
    Manage an influx db connection
    """

    def __init__(self, config):
        self.config = config
        self.redis = redis.StrictRedis(
            self.config['REDIS_HOST'],
            int(self.config['REDIS_PORT']),
            encoding="utf-8",
            decode_responses=True
        )

    def _tag_from_name(self, vehicle_name):
        return vehicle_name + "_state"

    def get_vehicle_state(self, vehicle_name):
        """
        :param vehicle_name:
        :return: key,value dict of state variables.
        """
        return self.redis.hgetall(self._tag_from_name(vehicle_name))

    def del_vehicle_state(self, vehicle_name):
        keys = tuple(self.redis.hgetall(self._tag_from_name(vehicle_name)).keys())
        if len(keys) > 0:
            self.redis.hdel(self._tag_from_name(vehicle_name), *keys)

    def set_vehicle_state(self, vehicle_name, state_dict):
        tag = self._tag_from_name(vehicle_name)
        for key in state_dict.keys():
            self.redis.hset(tag, key, state_dict[key])
