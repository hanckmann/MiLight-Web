from flask import render_template, request
from flask_api import status
import json
import datetime

from app import app

# import the Milight MCI package if possible
try:
    # Use this if the milight-mci.egg is installed
    import mci
    import mci_parser
except:
    try:
        # Use this if the milight-mci.egg is not installed
        import os
        milight_path = '../MiLight-Control-Interface/'
        if 'MILIGHT_PATH' in os.environ:
            milight_path = os.environ['MILIGHT_PATH']
        else:
            print('WARNING: Please set your MILIGHT_PATH environment variable to the MiLight-Control-Interface project-folder (make sure it is exported).')

        import inspect
        import sys
        # include modules from a subforder
        cmd_subfolder = os.path.realpath(
            os.path.abspath(os.path.join(os.path.split(
                inspect.getfile(inspect.currentframe()))[0],
                os.path.join(milight_path))))
        if cmd_subfolder not in sys.path:
            sys.path.insert(0, cmd_subfolder)
        import mci
        import mci_parser
    except ImportError as e:
        print('ERROR: Could not import the MiLight-Control-Interface package.')
        sys.exit()

# Populate the bridges dict
bridges = list()
bridges_time = datetime.datetime.now()


@app.route('/')
@app.route('/index')
def index():
    """ Landing page """
    return render_template('index.html')


@app.route('/milight', methods=['POST'])
def put_milight():
    """ Support for PUT/POST commands """
    bridge = request.form['bridge']
    bulb = request.form['bulb']
    group = request.form['group']
    action = request.form['action']
    value = request.form['value']
    bridge = bridge.replace('string:','')
    action = action.replace('string:','')
    bulb = bulb.replace('number:1','RGBW')
    bulb = bulb.replace('number:2','WHITE')
    return route_milight(bridge, bulb, group, action, value)


@app.route('/milight/<bridge>/<bulb>/<group>/<action>')
def route_milight_no_value(bridge, bulb, group, action):
    """ Direct access interface (REST) """
    return route_milight(bridge, bulb, group, action, None)


@app.route('/milight/<bridge>/<bulb>/<group>/<action>/<value>')
def route_milight(bridge, bulb, group, action, value):
    """ Direct access interface (REST) """
    # Parse and validate all input
    print('bridge=' + str(bridge) + '\tbulb=' + str(bulb) + '\tgroup=' + str(group) + '\taction=' + str(action) + '\tvalue=' + str(value))
    try:
        mci_parser.validate_command(bridge, bulb, group, action, value)
    except Exception as e:
        err = str(e)
        return json.dumps({'validation error': str(err)}), status.HTTP_404_NOT_FOUND

    mci_parser.execute_command(bridge, bulb, group, action, value)
    return return json.dumps({'status': 'success'})


@app.route('/milight/scan')
def route_milight_scan():
    """ scan for bridges """
    global bridges
    global bridges_time
    discovered = mci.DiscoverBridge(port=48899).discover()
    bridges_time = datetime.datetime.now()
    bridges = list()
    for db in discovered:
        bridges.append(db[0])
    return route_milight_bridges()


@app.route('/milight/bridge')
@app.route('/milight/bridges')
def route_milight_bridges():
    """ Provide available bridges """
    time_difference = (datetime.datetime.now() - bridges_time).seconds
    if not bridges:
        if time_difference > 15:
            return route_milight_scan()
        else:
            bridges.append('none-tmp')
    return json.dumps({'bridges': bridges, 'time': str(bridges_time)})


@app.route('/milight/color')
@app.route('/milight/colors')
def route_get_colors():
    """ Get the color codes """
    return json.dumps([color for color in mci.ColorGroup.COLOR_CODES.keys()])


@app.route('/milight/disco')
def route_get_disco():
    """ Get the disco codes """
    return json.dumps([code for code in mci.ColorGroup.DISCO_CODES.keys()])
