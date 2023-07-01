from flask import Flask
 
# Flask constructor takes the name of current module (__name__) as argument.
app = Flask(__name__)
 
# The route() function of the Flask class tells the application which URL should call the associated function.

@app.route('/')
# ‘/’ URL is bound with hello_world() function.

def hello_world():
    return 'Hello World'

@app.route('/web')
# ‘/web’ URL is bound with web() function.

def web():
    return 'Hello Web'

# browser: localhost:5000/web
 
# main driver function
if __name__ == '__main__':
 
    # run() method of Flask class runs the application on the local development server.
    # browser: localhost:5000
    app.run()