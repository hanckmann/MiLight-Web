from flask import render_template, request
from flask_api import status
import json
import datetime
import os

import mci.bridges
import mci.bulbs
import mci.mci_parser

from app import app


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
    bridge = bridge.replace('string:', '')
    action = action.replace('string:', '')
    bulb = bulb.replace('number:1', 'RGBW')
    bulb = bulb.replace('number:2', 'WHITE')
    return route_milight(bridge, bulb, group, action, value)


@app.route('/milight/json', methods=['POST'])
def route_milight_json():
    """ Json interface (REST) """
    # print(str(request.json))
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
    # print('bridge=' + str(bridge) + '\tbulb=' + str(bulb) + '\tgroup=' +
    #       str(group) + '\taction=' + str(action) + '\tvalue=' + str(value))
    try:
        mci.mci_parser.validate_command(bridge, bulb, group, action, value)
    except Exception as e:
        return json.dumps({'validation error': str(e)}), status.HTTP_404_NOT_FOUND

    mci.mci_parser.execute_command(bridge, bulb, group, action, value)
    return json.dumps({'status': 'success'})


@app.route('/milight/scan')
def route_milight_scan():
    """ scan for bridges """
    global bridges
    global bridges_time
    discovered = mci.bridges.DiscoverBridge(port=48899).discover()
    bridges_time = datetime.datetime.now()
    bridges = list()
    for db in discovered:
        bridges.append(db[1])
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
    return json.dumps([color for color in mci.bulbs.ColorGroup.COLOR_CODES.keys()])


@app.route('/milight/disco')
def route_get_disco():
    """ Get the disco codes """
    return json.dumps([code for code in mci.bulbs.ColorGroup.DISCO_CODES.keys()])


# Settings
settings_file = '/tmp/settings.json'


@app.route('/settings', methods=['GET', 'POST'])
def settings_route():
    """ View and change settings """
    if request.method == 'GET':
        route_milight_scan()
        bridges.append('dummy-bridge')
        if os.path.isfile(settings_file):
            with open(settings_file) as file:
                settings = json.load(file)
                settings = json_to_settings(settings_to_json(settings))
        else:
            settings = json_to_settings()
        print('JSON DUMP')
        print(settings)
        return render_template('settings.html',
                               bridges=settings)
    if request.method == 'POST':
        settings = json_to_settings(request.json)
        with open(settings_file, 'w') as file:
            json.dump(settings, file, sort_keys=True)
        # print(json.dumps(settings, sort_keys=True))
        return json.dumps({'result': 'oke'})
    # Else
    return json.dumps({'result': 'No valid action'})


def json_to_settings(flat=dict()):
    """ JSON to settings-object """
    # print(flat)
    settings = list()
    for bridge in bridges:
        # Bulb settings
        rgbw_settings = dict()
        rgbw_settings['group'] = flat.get(bridge + '-rgbw-group', '')
        rgbw_settings['group-1'] = flat.get(bridge + '-rgbw-group-1', '')
        rgbw_settings['group-2'] = flat.get(bridge + '-rgbw-group-2', '')
        rgbw_settings['group-3'] = flat.get(bridge + '-rgbw-group-3', '')
        rgbw_settings['group-4'] = flat.get(bridge + '-rgbw-group-4', '')
        white_settings = dict()
        white_settings['group'] = flat.get(bridge + '-white-group', '')
        white_settings['group-1'] = flat.get(bridge + '-white-group-1', '')
        white_settings['group-2'] = flat.get(bridge + '-white-group-2', '')
        white_settings['group-3'] = flat.get(bridge + '-white-group-3', '')
        white_settings['group-4'] = flat.get(bridge + '-white-group-4', '')
        # Bridge settings
        bridge_settings = dict()
        bridge_settings['mac-address'] = bridge
        bridge_settings['name'] = flat.get(bridge + '-name', '')
        bridge_settings['rgbw'] = rgbw_settings
        bridge_settings['white'] = white_settings
        # Add to settings-object
        settings.append(bridge_settings)
    return settings


def settings_to_json(settings):
    """ Settings-object to JSON """
    flat = dict()
    remaining_bridges = [bridge for bridge in bridges]
    for bridge_settings in settings:
        # Bridge settings
        if 'mac-address' not in bridge_settings:
            print('ERROR: bridge MAC is not provided in the settings!')
            continue
        bridge = bridge_settings['mac-address']
        if bridge in remaining_bridges:
            remaining_bridges.remove(bridge)
        flat[bridge + '-name'] = bridge_settings.get('name', '')
        # Bulb settings
        if 'rgbw' not in bridge_settings:
            bridge_settings['rgbw'] = dict()
        flat[bridge + '-rgbw-group'] = bridge_settings['rgbw'].get('group', '')
        flat[bridge + '-rgbw-group-1'] = bridge_settings['rgbw'].get('group-1', '')
        flat[bridge + '-rgbw-group-2'] = bridge_settings['rgbw'].get('group-2', '')
        flat[bridge + '-rgbw-group-3'] = bridge_settings['rgbw'].get('group-3', '')
        flat[bridge + '-rgbw-group-4'] = bridge_settings['rgbw'].get('group-4', '')
        if 'white' not in bridge_settings:
            bridge_settings['white'] = dict()
        flat[bridge + '-white-group'] = bridge_settings['white'].get('group', '')
        flat[bridge + '-white-group-1'] = bridge_settings['white'].get('group-1', '')
        flat[bridge + '-white-group-2'] = bridge_settings['white'].get('group-2', '')
        flat[bridge + '-white-group-3'] = bridge_settings['white'].get('group-3', '')
        flat[bridge + '-white-group-4'] = bridge_settings['white'].get('group-4', '')
    for bridge in remaining_bridges:
        # Add a the bridges current info
        flat[bridge + '-name'] = ''
        flat[bridge + '-rgbw-group'] = ''
        flat[bridge + '-rgbw-group-1'] = ''
        flat[bridge + '-rgbw-group-2'] = ''
        flat[bridge + '-rgbw-group-3'] = ''
        flat[bridge + '-rgbw-group-4'] = ''
        flat[bridge + '-white-group'] = ''
        flat[bridge + '-white-group-1'] = ''
        flat[bridge + '-white-group-2'] = ''
        flat[bridge + '-white-group-3'] = ''
        flat[bridge + '-white-group-4'] = ''
    return flat
