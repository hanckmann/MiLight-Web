from flask import render_template, request, redirect
from flask_api import status
import json
import datetime
import os

import mci.bridges
import mci.bulbs
import mci.mci_parser

from app import app


# Populate the bridges dict
scan_time = datetime.datetime.now()
bridges = dict()  # bridges[mac] = ip
settings = list()
settings_file = '/tmp/settings.json'


@app.route('/')
@app.route('/index')
def route_redirect_index():
    """ We do not work on the index, but only on the sub-level milight """
    return redirect("/milight", code=302)


@app.route('/milight', methods=['GET'])
def index():
    """ Landing page """
    global bridges
    route_milight_scan()
    return render_template('index.html',
                           settings=settings)


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
    global bridges
    print(bridges)
    if bridge in bridges:
        bridge = bridges[bridge]
    # Parse and validate all input
    # print('bridge=' + str(bridge) + '\tbulb=' + str(bulb) + '\tgroup=' +
    #       str(group) + '\taction=' + str(action) + '\tvalue=' + str(value))
    try:
        mci.mci_parser.validate_command(bridge, bulb, group, action, value)
    except Exception as e:
        return json.dumps({'validation error': str(e)}), status.HTTP_404_NOT_FOUND

    mci.mci_parser.execute_command(bridge, bulb, group, action, value)
    return json.dumps({'status': 'success'})


# Get bridges

@app.route('/milight/scan')
def route_milight_scan():
    """ scan for bridges """
    global bridges
    global scan_time
    scan_time = datetime.datetime.now()
    discovered = mci.bridges.DiscoverBridge(port=48899).discover()
    bridges = dict()
    for (ip, mac) in discovered:
        bridges[mac] = ip
    global settings
    global settings_file
    settings = load_settings(settings_file)
    settings = update_settings(settings, list(bridges.keys()))
    return route_milight_bridges()


@app.route('/milight/bridge')
@app.route('/milight/bridges')
def route_milight_bridges():
    """ Provide available bridges """
    bridges = [setting['mac-address'] for setting in settings]
    return json.dumps({'bridges': bridges, 'time': str(scan_time)})


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

@app.route('/milight/settings', methods=['GET', 'POST'])
def route_settings():
    """ View and change settings """
    global settings
    if request.method == 'GET':
        route_milight_scan()
        return render_template('settings.html',
                               settings=settings)
    if request.method == 'POST':
        print('SETTINGS POST')
        settings = json_to_settings(settings, request.json)
        save_settings(settings, settings_file)
        return json.dumps({'result': 'oke'})
    # Else
    return json.dumps({'result': 'No valid action'})


@app.route('/milight/settings/<bridge>')
def route_get_settings_bridge(bridge):
    """ Get the settings for a bridge """
    setting = [setting for setting in settings if setting['mac-address'] == bridge]
    return json.dumps(setting[0])


def save_settings(settings, filename):
    """ Save the settings-object to file """
    with open(filename, 'w') as file:
        json.dump(settings, file, sort_keys=True)


def load_settings(filename):
    """ Load the settings-object from file (and extend if required) """
    global bridges
    settings = list()
    if os.path.isfile(filename):
        with open(filename) as file:
            settings = json.load(file)
            settings = json_to_settings(settings, settings_to_json(settings, bridges))
    return settings


def update_settings(settings, bridges):
    """ Init an empty settings-object """
    settings_macs = [setting['mac-address'] for setting in settings]
    new_bridges = [bridge for bridge in bridges if bridge not in settings_macs]
    for bridge in new_bridges:
        # Bulb settings
        rgbw_settings = dict()
        rgbw_settings['group'] = 'ALL'
        rgbw_settings['group-1'] = '1'
        rgbw_settings['group-2'] = '2'
        rgbw_settings['group-3'] = '3'
        rgbw_settings['group-4'] = '4'
        white_settings = dict()
        white_settings['group'] = 'ALL'
        white_settings['group-1'] = '1'
        white_settings['group-2'] = '2'
        white_settings['group-3'] = '3'
        white_settings['group-4'] = '4'
        # Bridge settings
        bridge_settings = dict()
        bridge_settings['mac-address'] = bridge
        bridge_settings['name'] = bridge
        bridge_settings['rgbw'] = rgbw_settings
        bridge_settings['white'] = white_settings
        # Add to settings-object
        settings.append(bridge_settings)
    return settings


def json_to_settings(settings, setting_form=dict()):
    """ JSON to settings-object """
    mac_addresses = [setting['mac-address'] for setting in settings]
    for setting_key, setting_value in setting_form.items():
        # Split into three: bridge | <bulbtype> | group(s)
        identifier = setting_key.split("-")
        if not identifier:
            print('ERROR: identifier undefined; ->' + str(setting_key))
            continue
        # Check if the mac-address is known
        mac_address = identifier[0]
        if mac_address not in mac_addresses:
            print('ERROR: mac_address not in mac_addresses; ->' + str(setting_key))
            continue
        # Check if a name is provided
        if len(identifier) == 2:
            if not identifier[1] == 'name':
                print('ERROR: len(identifier) != 2; identifier[1] != "name"; ->' + str(setting_key))
                continue
            setting = [setting for setting in settings if setting['mac-address'] == mac_address][0]
            setting['name'] = setting_value
            continue
        # Check the bulb-type and group(s)
        if len(identifier) >= 3:
            bulbtype = ['rgbw', 'white']
            if identifier[1] not in bulbtype:
                print('ERROR: identifier[1] not in bulbtype; ->' + str(setting_key))
                continue
            setting = [setting for setting in settings if setting['mac-address'] == mac_address][0]
            bulb_setting = setting[identifier[1]]
            groups = ['1', '2', '3', '4']
            if len(identifier) == 3:
                bulb_setting['group'] = setting_value
                continue
            elif len(identifier) == 4:
                if identifier[3] not in groups:
                    print('ERROR: identifier[3] not in groups; ->' + str(setting_key))
                    continue
                bulb_setting['group-' + identifier[3]] = setting_value
                continue
        print('ERROR: identifier has invalid length ->' + str(setting_key))
    return settings


def settings_to_json(settings, bridges):
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
