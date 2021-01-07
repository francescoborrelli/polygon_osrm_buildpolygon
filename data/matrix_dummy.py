from flask import Blueprint, request, jsonify
import pytz
import datetime
import math

dummy_bp = Blueprint('dummy_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@dummy_bp.route('/restart', methods=['GET', 'POST'])
def restart():
    if request.method=="GET":
        return jsonify ({'status':'ok'}), 200
    elif request.method=="POST":
        return "Restarting"


@dummy_bp.route('/can_reinstall', methods=['POST'])
def can_reinstall():
    try:
        return jsonify({'status': 'sucess'}) , 200
    except BaseException as e:
        print(e)
        return jsonify({'error': str(e)}), 500


QUEUE = 'queue:messages'
DEFAULT_MAX = 3000
MAX_NUM = 'max_num'
MAX_REDIS_MESSAGES = 1000*1000



@dummy_bp.route('/data', methods=['GET', 'POST'])
def data():
    if request.method == 'GET':
        messages = []
        return jsonify ({'messages':messages}), 200


VEHICLE_NAME='vehicle_name'
@dummy_bp.route("/vehicle_state", methods=["GET","POST"])
def vehicle_state():
    """
    Set/get state of vehicle data system from onboard computer.
    :return:
    """

    if request.method == 'GET':
        ts = ((datetime.datetime.now().astimezone(pytz.utc) -datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds())
        ns = int(ts) * int(math.pow(10,9))
        data = {
            'vehicle_name': "a car",
            'time': ns,
            'last_can_time': ns,
            'last_gps_time': ns
        }
        return jsonify(data ) , 200
    elif request.method == 'POST':
        data = request.json
        return jsonify({'status': 'success'}), 200