#!/usr/bin/env python

import urllib
import json
import os
import requests

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "ServiceStatus":
        return {}
    resp = requests.get('http://demo3589489.mockable.io/realtime/serviceStatus')
    result = req.get("result")
    parameters = result.get("parameters")
    mode = parameters.get("Travelmode")
    if resp.status_code != 200:
        # This means something went wrong.
        raise ApiError('GET /tasks/ {}'.format(resp.status_code))
    output = [routeDetails for routeDetails in resp.json()["routeDetails"] if
              (routeDetails["route"] == 'M66' and routeDetails['mode'] == mode)]

    print (output[0].get("inService"))
    print (output[0].get("statusDetails")[0]["statusSummary"])

    res = makeWebhookResult(output)
    return res


def makeWebhookResult(output):


    speech = "Today " + output[0].get("route") + ": " + output[0].get("statusDetails")[0]["statusSummary"]

    print("Response:")
    print(speech)


    return {
        "speech": speech,
        "displayText": speech,

        "source": "mta-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % (port))

    app.run(debug=False, port=port, host='0.0.0.0')