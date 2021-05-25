#!/usr/bin/env python

import logging
from flask import Flask, jsonify, request
from vm import VM
from host import HOST

app = Flask(__name__)

format = "%(asctime)s: %(levelname)s : %(message)s"
logging.basicConfig(format=format, level=logging.DEBUG,
                    datefmt="%H:%M:%S")

''' example payload
curl -i -d '{
    "hostIp": "127.0.0.1",
    "hostPass": "xxxxxx",
    "hostUser": "root",
    "vmAction": "create",
    "vmMemory": 4096,
    "vmDisk": 20,
    "vmName": "test-1",
    "vmType": "centos7",
    "vmVcpus": 2
}' -H "Content-Type: application/json" -X POST http://localhost:9134/vm
'''


@app.route('/vm', methods=['POST'])
def vm_action():
    payload = request.get_json()
    logging.debug(payload)

    field = {'hostIp', 'hostUser', 'hostPass', 'vmName', 'vmAction'}
    if field - set(payload.keys()):
        error_msg = "Input json missing some field! " + "It must include " + str(field)
        logging.error(error_msg)
        return jsonify({"error": error_msg}), 400
    else:
        action = payload['vmAction']
        try:
            vm = VM(payload['hostIp'], payload['hostUser'], payload['hostPass'], payload['vmName'])
            if action == 'create':
                vm.vcpus = payload['vmVcpus']
                vm.memory = payload['vmMemory']
                vm.disk = payload['vmDisk']
                vm.os_type = payload['vmType']
                # optional params
                if "rootPass" in payload.keys() and payload['rootPass']:
                    vm.root_pass = payload['rootPass']
                if "vncPass" in payload.keys() and payload['vncPass']:
                    vm.vnc_pass = payload['vncPass']
                if "vmHostname" in payload.keys() and payload['vmHostname']:
                    vm.hostname = payload['vmHostname']
                else:
                    vm.hostname = payload['vmName']
                logging.info("VM creating")
                vm.create()
                logging.info("VM created")
            elif action == 'start':
                vm.start()
            elif action == 'shutdown':
                vm.shutdown()
            elif action == 'reboot':
                vm.reboot()
            elif action == 'delete':
                vm.delete()
            else:
                error_msg = "give vmAction: {} not support".format(action)
                return jsonify({"error": error_msg}), 400

        except Exception as e:
            logging.error(str(e))
            return jsonify({"error": str(e)}), 500

    return jsonify(""), 202


# example: curl -X GET http://localhost:9134/vm?vmName=test\&hostIp=127.0.0.1\&hostPass=xxxxx\&hostUser=root
@app.route('/vm', methods=['GET'])
def vm_reader():
    data = {}
    payload = request.args
    logging.debug(payload)

    field = {'hostIp', 'hostUser', 'hostPass', 'vmName'}
    if field - set(payload.keys()):
        error_msg = "Input json missing some field! " + "It must include " + str(field)
        logging.error(error_msg)
        return jsonify({"error": error_msg}), 400
    else:
        try:
            vm = VM(payload['hostIp'], payload['hostUser'], payload['hostPass'], payload['vmName'])
            data['name'], data['status'], data['address'], data['vncPort'] = vm.get_info()
        except Exception as e:
            logging.error(str(e))
            return jsonify({"error": str(e)}), 500

    return jsonify(data), 200


''' example payload
curl -i -d '{
    "Ip": "127.0.0.1",
    "Pass": "xxxxxx",
    "User": "root",
    "Role": "compute",
    "Action": "install"
}' -H "Content-Type: application/json" -X POST http://localhost:9134/host
'''


@app.route('/host', methods=['POST'])
def host_action():
    data = {}
    payload = request.get_json()
    logging.debug(payload)

    field = {'Ip', 'User', 'Pass', 'Role', 'Action'}
    if field - set(payload.keys()):
        error_msg = "Input json missing some field! " + "It must include " + str(field)
        logging.error(error_msg)
        return jsonify({"error": error_msg}), 400
    else:
        try:
            host = HOST(payload['Ip'], payload['User'], payload['Pass'], payload['Role'])
            if payload['Action'] == 'install':
                logging.info("HOST installation is started")
                data['cpu'], data['memory'], data['disk'], data['type'] = host.install()
                logging.info("HOST installation is done")

        except Exception as e:
            logging.error(str(e))
            return jsonify({"error": str(e)}), 500

    return jsonify(data), 200


# example: curl -X GET http://localhost:9134/host?Ip=127.0.0.1\&Pass=xxxxx\&User=root
@app.route('/host', methods=['GET'])
def host_reader():
    data = {}
    payload = request.args
    logging.debug(payload)

    field = {'Ip', 'User', 'Pass'}
    if field - set(payload.keys()):
        error_msg = "Input json missing some field! " + "It must include " + str(field)
        logging.error(error_msg)
        return jsonify({"error": error_msg}), 400
    else:
        try:
            host = HOST(payload['Ip'], payload['User'], payload['Pass'])
            data['cpu'], data['memory'], data['disk'], data['type'] = host.get_info()
        except Exception as e:
            logging.error(str(e))
            return jsonify({"error": str(e)}), 500

    return jsonify(data), 200


''' example payload
curl -i -d'{
    "Ip": "127.0.0.1",
    "Pass": "xxxxxxx",
    "User": "root",
    "rules": [
      {
        "dport": "32346",
        "destination": "192.168.122.89:22",
        "state": "present",
        "protocol": "tcp"
      }
    ]
}' -H "Content-Type: application/json" -X POST http://localhost:9134/host/dnat
'''


@app.route('/host/dnat', methods=['POST'])
def port_dnat():
    payload = request.get_json()
    logging.debug(payload)

    field = {'Ip', 'User', 'Pass', 'rules'}
    if field - set(payload.keys()):
        error_msg = "Input json missing some field! " + "It must include " + str(field)
        logging.error(error_msg)
        return jsonify({"error": error_msg}), 400
    else:
        try:
            host = HOST(payload['Ip'], payload['User'], payload['Pass'])
            host.port_dnat(payload['rules'])
        except Exception as e:
            logging.error(str(e))
            return jsonify({"error": str(e)}), 500

    return jsonify(""), 202


if __name__ == "__main__":
    try:
        app.run(debug=False, host='::', port=9134)
    except Exception as e:
        logging.error(e)
