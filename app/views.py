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
    route_milight_scan()
    return render_template('index.html',
                           bridges=bridges)


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


@app.route('/milight/json', methods=['POST'])
def route_milight_json():
    """ Json interface (REST) """
    print(str(request.json))
    try:
        return route_milight(request.json['bridge'],
                             request.json['bulb'],
                             request.json['group'],
                             request.json['action'],
                             request.json['value'])
    except KeyError as e:
        print(json.dumps({'error': str(e)}))
        return json.dumps({'error': str(e)})
    except Exception as e:
        print(json.dumps({'validation error': str(e)}))
        return json.dumps({'validation error': str(e)})


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
        return json.dumps({'validation error': str(e)}), status.HTTP_404_NOT_FOUND

    mci_parser.execute_command(bridge, bulb, group, action, value)
    return json.dumps({'status': 'success'})


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


# Get available actions

@app.route('/milight/action_rgbw')
def route_get_action_rgbw():
    """ Get the color codes """
    return json.dumps(['on', 'off', 'white', 'brightness', 'disco', 'increase_disco_speed', 'decrease_disco_speed', 'color'])


@app.route('/milight/action_white')
def route_get_action_white():
    """ Get the color codes """
    return json.dumps(['on', 'off', 'increase_brightness', 'decrease_brightness', 'increase_warmth', 'decrease_warmth', 'brightmode', 'nightmode'])


# Get valid values

@app.route('/milight/values_on')
@app.route('/milight/values_off')
@app.route('/milight/values_white')
@app.route('/milight/values_brightmode')
@app.route('/milight/values_nightmode')
def route_get_values_none():
    """ There is not expected value """
    return json.dumps(None)


@app.route('/milight/values_brightness')
def route_get_values_0_25():
    """ Expected value: 0 <= value ,= 25 """
    return json.dumps([0, 25])


@app.route('/milight/values_brightness')
@app.route('/milight/values_increase_disco_speed')
@app.route('/milight/values_decrease_disco_speed')
@app.route('/milight/values_increase_brightness')
@app.route('/milight/values_decrease_brightness')
@app.route('/milight/values_increase_warmth')
@app.route('/milight/values_decrease_warmth')
def route_get_values_1_30():
    """ Expected value: 1 <= value ,= 30 """
    return json.dumps([1, 30])


@app.route('/milight/color')
@app.route('/milight/colors')
def route_get_values_colors():
    """ Get the color codes """
    return json.dumps([color for color in mci.ColorGroup.COLOR_CODES.keys()])


@app.route('/milight/disco')
def route_get_disco():
    """ Get the disco codes """
    return json.dumps([code for code in mci.ColorGroup.DISCO_CODES.keys()])
