#!/usr/bin/env python

import logging
from flask import Flask, jsonify, request
from vm import VM

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
            data['name'], data['status'], data['address'] = vm.get_info()
        except Exception as e:
            logging.error(str(e))
            return jsonify({"error": str(e)}), 500

    return jsonify(data), 200


try:
    app.run(debug=False, host='::', port=9134)
except Exception as e:
    logging.error(e)
