#  Copyright (c) 2020. AV Connect Inc.
from unittest import TestCase
from data import redis_state

class TestRedisState(TestCase):
    def setUp(self) -> None:
        config = {'REDIS_HOST':'127.0.0.1', 'REDIS_PORT':'6379'}
        self.vehicle_name = "UnitTestVehicle"
        self.redis_state =  redis_state.RedisState(config)
        self.redis_state.del_vehicle_state(self.vehicle_name)

    def testSetAndGet(self):
        state = {'one':'red', 'two':'blue'}
        self.redis_state.set_vehicle_state(self.vehicle_name, state)
        state_2 = self.redis_state.get_vehicle_state(self.vehicle_name)
        self.assertEqual(state, state_2)

    def testDel(self):
        state = {'one':'red', 'two':'blue'}
        self.redis_state.set_vehicle_state(self.vehicle_name, state)
        self.redis_state.del_vehicle_state(self.vehicle_name)
        self.assertEqual(self.redis_state.get_vehicle_state(self.vehicle_name),{})
