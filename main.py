import flask
import json
import os
from flask import send_from_directory, request

# Flask app should start in global layout
app = flask.Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/favicon.png')

@app.route('/')

@app.route('/home')
def home():
    return "Hello World"


@app.route('/webhook', methods=['GET','POST'])
def webhook():
    # req = request.get_json(force=True)
    # query_text = req.get('sessionInfo').get('parameters').get('query_text')


    try:
        req = outrequest
        # If the outrequest variable exists, the above line will assign its value to "req"
        # You can use "req" further in your code
    except NameError:
        # Handle the case when outrequest variable does not exist
        req = None
        print("outrequest variable does not exist.")

    # Now you can use "req" safely knowing that it is either assigned the value of "outrequest" or "None" if it was not defined


    text = "webhook text response"

    res = {
        "fulfillment_response": {"messages": [{"text": {"text": [text]}}]}
    }

    return res

if __name__ == "__main__":
    app.run()
#    app.debug = True