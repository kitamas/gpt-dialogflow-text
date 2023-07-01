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
    req = request.get_json(force=True)
    query_text = req.get('sessionInfo').get('parameters').get('query_text')

    text = "webhook text response"

    res = {
        "fulfillment_response": {"messages": [{"text": {"text": [query_text + " " + text]}}]}
    }

    return res

if __name__ == "__main__":
    app.run()
#    app.debug = True

"""
    if req is None:
        print("req is None.")
    else:
        # Access req or perform operations
        print("req:", req)

    
    try:
        req = request.get_json(force=True)
        # If the outrequest variable exists, the above line will assign its value to "req"
        # You can use "req" further in your code
    except NameError:
        # Handle the case when outrequest variable does not exist
        req = None
        print("outrequest variable does not exist.")

    # Now you can use "req" safely knowing that it is either assigned the value of "outrequest" or "None" if it was not     """