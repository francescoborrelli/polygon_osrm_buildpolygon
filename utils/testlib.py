from ws_maps.route import Origin, Destination, Engine
from ws_models.features.vep import Features
from ws_models.models.longitudinal import LongitudinalPerSegment
from ws_models.models.motor import Motor
from ws_models.models.auxiliary import Auxiliaries
from ws_models.models.ev import ElectricVehicle
from ws_models.models.driver import Driver
from ws_maps.network import Network


vehicle_name = "Grey_Kona"

origin = Origin(address='2120 McGee Ave, Berkeley, CA 94703')
origin3 = Origin(latitude=37.87186760458897, longitude=-122.26770753052297)
from datetime import datetime
destination = Destination(address='161 Steuart St, San Francisco, CA 94105')
destination3 = Destination(latitude=37.7917632, longitude=-122.3957311)
engine = Engine(network=Network())


start = datetime.now()
print(start)

# route = engine.route(origin, destination)
route = engine.route(origin, destination, matched=False)
#route.plot()

print("route time " + str(datetime.now() - start))

# load EV model
lon = LongitudinalPerSegment(id=vehicle_name)
mot = Motor(id=vehicle_name)
aux = Auxiliaries(id=vehicle_name)
ev = ElectricVehicle(longitudinal=lon, motor=mot, auxiliaries=aux, battery_capacity_kwh=64.0)

# load driver model
driver = Driver(id=vehicle_name)

# predict route consumption
prediction, summary = ev.predict(driver.predict(route))
print("the predicted decrease in SOC is {:.1f} %".format(summary.battery_soc_change))

print("Took " + str(datetime.now() - start))