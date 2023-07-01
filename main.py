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
    #req = request.get_json(force=True)
    

    try:
        if request.get_json(force=True) is None: # The variable
        # if val is None: # The variable
            # print('It is None')
    except NameError:
        # print ("This variable is not defined")
    else:
        # print ("It is defined and has a value")
        req = request.get_json(force=True)

    res = {
        "fulfillment_response": {"messages": [{"text": {"text": [text]}}]}
    }

    return res

if __name__ == "__main__":
    app.run()
#    app.debug = True