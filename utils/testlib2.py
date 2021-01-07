from ws_maps.route import Origin, Destination, Engine
from ws_models.features.vep import Features
from ws_models.models.longitudinal import LongitudinalPerSegment
from ws_models.models.motor import Motor
from ws_models.models.auxiliary import Auxiliaries
from ws_models.models.ev import ElectricVehicle
from ws_models.models.driver import Driver

vehicle_name = "Grey_Kona"


origin = Origin(address='2120 McGee Ave, Berkeley, CA 94703')
destination = Destination(address='161 Steuart St, San Francisco, CA 94105')
engine = Engine(bbid='upper-sf-bay-new')
route = engine.route(origin, destination)
#route.plot()
# load features
features = Features(['distance_change', 'tire_pressure_sqrt_inv', 'speed_initial', 'speed_final', 'speed_variance',
                     'speed_skew', 'elevation_change', 'duration_change', 'wheel_energy_change',
                     'range_change', 'range_initial', 'soc_initial', 'soc_change', 'speed_mean',
                     'battery_energy_change', 'motor_electrical_energy_change', 'motor_mechanical_energy_change',
                     'cabin_temperature_setpoint_mean', 'cabin_temperature_mean', 'outside_temperature_mean',
                     'auxiliaries_power_mean', 'acceleration_max', 'acceleration_min'],
                    vehicle_name, aggregation='arc')

# load EV model
lon = LongitudinalPerSegment(features=features.data, id=vehicle_name)
lon.train()
lon.test()
lon.dump()
mot = Motor(features=features.data, id=vehicle_name)
mot.train()
mot.test()
mot.dump()
aux = Auxiliaries(features=features.data, id=vehicle_name)
aux.train()
aux.test()
aux.dump()
ev = ElectricVehicle(longitudinal=lon, motor=mot, auxiliaries=aux, battery_capacity_kwh=64.0)

# load driver model
driver = Driver(features.data, id=vehicle_name)
driver.train()
driver.dump()

# predict route consumption
prediction, summary = ev.predict(driver.predict(route))
print("the predicted decrease in SOC is {:.1f} %".format(summary.battery_soc_change))

