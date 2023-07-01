import flask
import json
import os
from flask import send_from_directory, request
# import openai
# import pinecone


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

    # Set your "OPENAI_API_KEY" Environment Variable in Heroku
    import openai

    openai.api_key = os.environ["OPENAI_API_KEY"]
    # openai.api_key = os.environ.get["OPENAI_API_KEY"]
    # openai.api_key = os.getenv("OPENAI_API_KEY")

    PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
    YOUR_ENV = os.environ['YOUR_ENV']

    intro_text = "Egy Telekom ügyfélszolgálatos asszisztens beszélget az ügyfelekkel. Válaszolj a kérdésekre a következő context alapján."

    # initializing a Pinecone index
    import pinecone

    # connect to pinecone environment
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=YOUR_ENV
    )

    index_name = "chat-doc-ts"

    index = pinecone.Index(index_name)


    req = request.get_json(force=True)
    query_text = req.get('sessionInfo').get('parameters').get('query_text')

    # ITT

    similar_questions = retrieve(query_text)

    # ITT

    text = "webhook text response"

    res = {
        "fulfillment_response": {"messages": [{"text": {"text": [query_text + " " + similar_questions]}}]}
    }

    return res


def retrieve(query):
    res = openai.Embedding.create(
        input=[query],
        engine=embed_model
    )
    # retrieve from Pinecone
    xq = res['data'][0]['embedding']

    # get relevant contexts
    res = index.query(xq, top_k=3, include_metadata=True)

    print("\nThe most similar questions:")
    for match in res['matches']:
        print(f"{match['score']:.2f}: {match['metadata']['text']}")

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