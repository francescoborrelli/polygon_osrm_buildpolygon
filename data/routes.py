"""Logged-in page routes."""
import traceback
from datetime import datetime

import pytz
from flask import Blueprint, render_template, redirect, url_for, jsonify, request, current_app
from flask_jwt_extended import jwt_required
from flask_login import current_user, login_required, logout_user
from . import models, charge_stations
from .telematics import Telematics
from .protocol import *
from .redis_state import RedisState

from ws_maps.route import Origin, Destination, Engine
from ws_models.models.longitudinal import LongitudinalPerSegment
from ws_models.models.motor import Motor
from ws_models.models.auxiliary import Auxiliaries
from ws_models.models.ev import ElectricVehicle
from ws_models.models.driver import Driver
from ws_maps.network import Network

# Blueprint Configuration
from .request_utils import *

# print("Creating Engine")
# # __upper_sf_bay_new_engine__= None
# __upper_sf_bay_new_engine__= Engine(bbid="upper-sf-bay-new")
# # __chino_engine__ = Engine(bbid='chino')
#
# def _engine():
#     return __upper_sf_bay_new_engine__
#     # return __chino_engine__

# print("Engine ready")

data_bp = Blueprint('main_bp', __name__,
                    template_folder='templates',
                    static_folder='static')

__telematics__ = None

def _telematics():
    global __telematics__
    if __telematics__ is None:
        __telematics__ = Telematics(current_app.config)
    return __telematics__

__shared_state__ = None
def _redis():
    global __shared_state__
    if __shared_state__ is None:
        __shared_state__ = RedisState(current_app.config)
    return __shared_state__

@data_bp.route('/', methods=['GET'])
@login_required
def dashboard():
    """Logged-in User Dashboard."""
    return render_template('dashboard.jinja2',
                           title='Flask-Login Tutorial.',
                           template='dashboard-template',
                           current_user=current_user,
                           body="You are now logged in!")


@data_bp.route("/logout")
@login_required
def logout():
    """User log-out logic."""
    logout_user()
    return redirect(url_for('auth_bp.login'))


@data_bp.route("/hello")
def hello():
    """Say hello to everyone"""
    return jsonify({"hello": 32}), 200


@data_bp.route("/drivers", methods=['GET', 'POST'])
@jwt_required
def driver():
    """Get or Add Drivers"""
    if request.method == "GET":
        drivers = models.Driver.query.all()
        return_drivers = [found_driver.name for found_driver in drivers]
        return jsonify(return_drivers), 200
    if request.method == "POST":
        data = request.json
        drivers_added = 0
        for driver in data['drivers']:
            found = models.Driver.query.filter(models.Driver.name == driver).first()
            if not found:
                models.db.session.add(models.Driver(name=driver))
                drivers_added += 1
            if drivers_added > 0:
                models.db.session.commit()

        return jsonify({"result": "added drivers " + str(drivers_added)}), 200


@data_bp.route("/vehicles", methods=['GET', 'POST'])
@jwt_required
def vehicles():
    """Get or Add Vehicles"""
    if request.method == "GET":
        vehicles = models.Vehicle.query.all()
        return_vehicles = [vehicle.name for vehicle in vehicles]
        return jsonify(return_vehicles), 200
    if request.method == "POST":
        data = request.json
        vehicles_added = 0
        for vehicle_name in data[VEHICLES]:
            found = models.Driver.query.filter(models.Vehicle.name == vehicle_name).first()
            if not found:
                vehicle_name = models.Vehicle
                vehicle_name.name = vehicle_name
                models.db.session.add(vehicle_name)
                vehicles_added += 1
            if vehicles_added > 0:
                models.db.session.commit()

        return jsonify({"result": "added drivers " + str(vehicles_added)}), 200


@data_bp.route("/latest_soc", methods=['GET'])
@jwt_required
def latest_soc():
    """ Get the latest SOC value from a vehicle and the time it was written"""
    if request.method == 'GET':
        ok, error = check_get_args([VEHICLE_NAME])
        if ok:
            vehicle_name = request.args.get(VEHICLE_NAME, False)
            # todo - create an soc tag for each type of car.
            soc_tag = "CR_Bms_Soc_Pc"
            data = _telematics().get_latest_from(vehicle_name, [soc_tag])
            print(data)
            if len(data) > 0 and soc_tag in data[0]:
                return jsonify({SOC: data[0][soc_tag], ISO_TIME: data[0]['time']}), 200
            else:
                return jsonify({"soc": -1, "time": "None"}), 200
        else:
            return error, 400


@data_bp.route("/drive_data", methods=['GET', 'POST'])
@jwt_required
def drive_data():
    """ Post to or get data from influx."""
    if request.method == 'GET':
        ok, error = check_get_args([VEHICLE_NAME])
        if ok:
            vehicle_name = request.args.get(VEHICLE_NAME, False)
            data = _telematics().get_todays_data(vehicle_name, '*', pytz.timezone('US/Pacific'))
            result_list = list(data.get_points(vehicle_name))
            return jsonify(result_list), 200
        else:
            return error, 400
    elif request.method == 'POST':
        data = request.json
        vehicle = data[VEHICLE_NAME]
        if "messages" in data:
            for message in data["messages"]:
                _telematics().write_data(vehicle, message)
        else:
            Telematics(current_app.config).write_data(vehicle, data)
        return jsonify({"status": "success"}), 200

# @data_bp.route("/vehicle_state", methods=["GET","POST"])
# @jwt_required
# def vehicle_state():
#     """
#     Set/get state of vehicle data system from onboard computer.
#     :return:
#     """
#     if request.method == 'GET':
#         ok, error = check_get_args([VEHICLE_NAME])
#         if ok:
#             state = _redis().get_vehicle_state(request.args.get(VEHICLE_NAME, False))
#             return jsonify(state) , 200
#         else:
#             return error, 400
#     elif request.method == 'POST':
#         data, error = check_json_post_args([VEHICLE_NAME])
#         _redis().set_vehicle_state(data[VEHICLE_NAME], data)
#         return jsonify({'status': 'success'}), 200

@data_bp.route("/drive", methods=["POST", "GET"])
@jwt_required
def drive():
    if request.method == 'POST':
        data, error = check_json_post_args([VEHICLE_NAME, DRIVER_NAME])
        if not error:
            driver_name = data[DRIVER_NAME]
            driver = models.Driver.query.filter(models.Driver.name == driver_name).first()
            vehicle_name = data[VEHICLE_NAME]
            vehicle = models.Vehicle.query.filter(models.Vehicle.name == vehicle_name).first()

            drive = models.Drive()
            drive.driver_id = driver.id
            drive.vehicle = vehicle
            drive.date = datetime.now().astimezone(pytz.utc)
            models.db.session.add(drive)
            models.db.session.commit()
            return jsonify({'status': 'success'}), 200
        else:
            return error, 400
    elif request.method == 'GET':
        ok, error = check_get_args([VEHICLE_NAME])
        if ok:
            vehicle_name = request.get.args(VEHICLE_NAME, False)
            drives = models.Drive.query.filter(models.Drive.vehicle == vehicle_name)
            drives_dict = [drive.to_dict() for drive in drives]
            return jsonify({
                'drives': drives_dict
            }), 200
        else:
            return error, 400


@data_bp.route("/can_data", methods=['POST'])
@jwt_required
def can_data():
    """
    Push can data array to telematics db.
    """
    _telematics().write_array_data(request.json)
    return jsonify({'status':'success'}), 200


@data_bp.route("/api/v1.1/route_here", methods=['POST'])
@jwt_required
def route_here():
    if request.method == 'POST':
        # if FAST in request.json.keys() and request.json[FAST]:
        #     return route_estimate()
        data, error = check_json_post_args([DESTINATION_LAT,
                                            DESTINATION_LON,
                                            SOURCE_LAT,
                                            SOURCE_LON,
                                            START_TIME,
                                            CHARGE_STATIONS_ORDERED,
                                            VEHICLE_NAME])
        if not error:
            #print("Data: " + str(data))
            origin = Origin(latitude=data[SOURCE_LAT], longitude=data[SOURCE_LON])
            destination = Destination(latitude=data[DESTINATION_LAT], longitude=data[DESTINATION_LON])
            charge_stations = data[CHARGE_STATIONS_ORDERED]
            print("Route from {},{} to {},{}".format(
                str(data[SOURCE_LAT]),
                str(data[SOURCE_LON]),
                str(data[DESTINATION_LAT]),
                str(data[DESTINATION_LON])
            ) )
            # todo - always use vehicle name
            data[VEHICLE_NAME] = 'Grey_Kona'
            try:
                engine = Engine(network=Network())
                route = engine.route(origin, destination, matched=False)
                lon = LongitudinalPerSegment(id=data[VEHICLE_NAME])
                mot = Motor(id=data[VEHICLE_NAME])
                aux = Auxiliaries(id=data[VEHICLE_NAME])
                ev = ElectricVehicle(longitudinal=lon, motor=mot, auxiliaries=aux, battery_capacity_kwh=64.0)

                # load driver model
                driver = Driver(id=data[VEHICLE_NAME])

                # predict route consumption
                prediction, summary = ev.predict(driver.predict(route))
                print("Expected soc change: {}".format(str(summary.battery_soc_change)))
                # charge_required = request.json['distance']*64.0/220.0
                return jsonify({#HERE_ROUTE: route._here_dict['json'],
                                CHARGE_USED_KWH: summary.battery_energy_change/1000/1000,
                                SOC_CHANGE_PCT: -1*summary.battery_soc_change,
                                # todo: get out of here route.
                                DISTANCE_MILES: 10,
                                ARRIVAL_TIME_ISO_8601: 'dummy_time'
                                }), 200
            except BaseException as e:
                print(e.__class__)
                print(e)
                traceback.print_tb(e.__traceback__)
                return jsonify({"result":"Not Routable",
                                "from": "{},{}".format(data[SOURCE_LAT],data[SOURCE_LON]),
                                "to": "{},{}".format(data[DESTINATION_LAT], data[SOURCE_LON]),
                                "error": str(traceback.format_tb(e.__traceback__))
                }), 200
        else:
            return error, 400

@data_bp.route("/route_estimate", methods=['POST'])
@jwt_required
def route_estimate():
    if request.method == 'POST':
        charge_required = request.json['distance']*64.0/220.0
        return jsonify({'kw_charge_required': charge_required, SOC_CHANGE_PCT: charge_required})

@data_bp.route("/api/v1.1/charge_stations", methods=["GET","POST"])
@data_bp.route("/charge_stations", methods=["GET","POST"])
@jwt_required
def get_charge_stations():
    """
    Given a route, get charge stations along that route.
    param: ?WAYPOINTS=lat1,lon1;lat2,lon2;lat3,lon3 ..
    returns: NREL JSON
    """
    waypoints_string = None
    if request.method == 'POST':
        data, error = check_json_post_args([WAYPOINTS])
        if data:
            waypoints_string = data[WAYPOINTS]
        else:
            return error, 400
    elif request.method == 'GET':
        ok, error = check_get_args([WAYPOINTS])
        if ok:
            waypoints_string = request.args.get(WAYPOINTS, False)
        else:
            return error, 400

    waypoints = [ [point.split(",")[0],point.split(",")[1]] for point in waypoints_string.split(";")]
    stations = charge_stations.get_charge_stations(current_app.config, waypoints)
    print(stations)
    return jsonify(
        stations
    ), 200
