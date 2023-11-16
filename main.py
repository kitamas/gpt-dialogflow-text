import flask
import json
import os
from flask import send_from_directory, request
import openai
import pinecone

# namespace = "infmuz"
namespace = "kando"
# namespace = "kumamoto"

index_name = "chat-doc-mt"

# Heroku config vars
openai.api_key = os.getenv("OPENAI_API_KEY")
# openai.api_key = "sk- . . ."

# Heroku config vars
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# TELEKOM PINECONE_API_KEY = "c47d17e1-62da-4f4a-a319-9608e3104d13"
# PINECONE_API_KEY = "a2a86279-ffc8-490c-9365-0d3d32a458a5"

# Heroku config vars
YOUR_ENV = os.getenv("YOUR_ENV")
# TELEKOM YOUR_ENV = "us-west1-gcp-free"
# YOUR_ENV = "us-west4-gcp"

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

def complete(prompt):
    messages = [{"role": "system", "content": "Kandó Kálmán Villamosmérnöki Kar. Az oktató ismerteti a tananyagot a hallgatókkal. Ha nem tudja a választ, mondja 'Nem tudom.'"},{"role": "user", "content": prompt}]
    # messages = [{"role": "system", "content": "Informatika Történeti Kiállítás, számítógépmúzeum. A tárlatvezető ismerteti a kiállítást a látogatóknak. Ha nem tudja a választ, mondja 'Nem tudom.'"},{"role": "user", "content": prompt}]
    # messages = [{"role": "system", "content": "Kumamoto University. The assistant answer the questions of students based on the prompt. If you do not know the answer, say 'I do not know.'"},{"role": "user", "content": prompt}]

    res = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = messages,
    temperature = 0.3,
    max_tokens = 500
    )

    return res["choices"][0]["message"]["content"]

# stop=["\n"],

@app.route('/webhook', methods=['GET','POST'])
def webhook():

    # Set your "OPENAI_API_KEY" Environment Variable in Heroku
    openai.api_key = os.environ["OPENAI_API_KEY"]

    PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
    YOUR_ENV = os.environ['YOUR_ENV']

    # initializing a Pinecone index
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=YOUR_ENV
    )

    index_name = "chat-doc-mt"

    index = pinecone.Index(index_name)

    req = request.get_json(force=True)

    query_text = req.get('sessionInfo').get('parameters').get('query_text')

    query_with_contexts = retrieve(query_text)

    answer = complete(query_with_contexts)

    res = {
        "fulfillment_response": {"messages": [{"text": {"text": [answer]}}]}
    }

    return res


embed_model = "text-embedding-ada-002"

# namespace_name = "infmuz"
namespace_name = "kando"
# namespace_name = "kumamoto"

def retrieve(query_text):
    index_name = "chat-doc-mt"

    index = pinecone.Index(index_name)

    res = openai.Embedding.create(
        input=[query_text],
        engine=embed_model
    )
    # retrieve from Pinecone
    xq = res['data'][0]['embedding']

    # get relevant contexts
    # res = index.query(xq, top_k=3, include_metadata=True)
    # res = index.query(xq, top_k=2, include_metadata=True)
    res = index.query(xq, top_k=2, include_metadata=True,namespace=namespace_name)

    """
    print("\nThe most similar questions:")
    for match in res['matches']:
    #    print(f"{match['score']:.2f}: {match['metadata']['text']}")
         similar_questions = match['metadata']['text']
    """

    contexts = [
        x['metadata']['text'] for x in res['matches']
    ]

    # limit = 3750 TIMEOUT ??
    limit = 3750

    # build our prompt with the retrieved contexts included
    prompt_start = (
        # "Kumamoto University. The assistant answers the questions of students, based on the context. Context: "
        "Kandó Kálmán Villamosmérnöki Kar. Az oktató ismerteti a tananyagot a hallgatókkal és válaszol a következő context alapján. Context: "
        # "Informatika Történeti Kiállítás, számítógépmúzeum. A tárlatvezető ismerteti a kiállítást és válaszol a látogatóknak a következő context alapján. Context: "
        # "Context:\n"
    )
    prompt_end = (
        #f"\n\nQuestion: {query_text}\nAnswer:"
        f"\n\nUser: {query_text}"
    )
    # append contexts until hitting limit
    for i in range(1, len(contexts)):
        if len("\n\n---\n\n".join(contexts[:i])) >= limit:
            prompt = (
                prompt_start +
                "\n---\n".join(contexts[:i-1]) +
                prompt_end
            )
            break
        elif i == len(contexts)-1:
            prompt = (
                prompt_start +
                "\n= = =\n".join(contexts) +
                prompt_end
            )

    return prompt


if __name__ == "__main__":

    app.run()
#    app.debug = True