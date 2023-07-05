import flask
import json
import os
from flask import send_from_directory, request
import openai
import pinecone

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
    # messages = [{"role": "system", "content": "You are a kind helpful assistant."},]
    messages = [{"role": "system", "content": "Informatika Történeti Kiállítás, számítógépmúzeum. A tárlatvezető ismerteti a kiállítást a látogatóknak."},{"role": "user", "content": prompt}]
    # messages = [{"role": "system", "content": "Egy Telekom ügyfélszolgálatos asszisztens beszélget az ügyfelekkel."}, {"role": "user", "content": prompt}]

    res = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = messages,
    temperature = 0.2,
    max_tokens = 200
    )

    return res["choices"][0]["message"]["content"]

# stop=["\n"],

"""
def complete(prompt):
    # print("PROMPT = ",prompt)
    res = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        temperature=0.2,
        max_tokens=250,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    return res['choices'][0]['text'].strip()
"""

@app.route('/webhook', methods=['GET','POST'])
def webhook():

    # Set your "OPENAI_API_KEY" Environment Variable in Heroku
    openai.api_key = os.environ["OPENAI_API_KEY"]

    PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
    YOUR_ENV = os.environ['YOUR_ENV']

    # intro_text = "Egy Telekom ügyfélszolgálatos asszisztens beszélget az ügyfelekkel. Válaszolj a kérdésekre a következő context alapján."
    # intro_text = "Informatika Történeti Kiállítás, számítógépmúzeum. A tárlatvezető ismerteti a kiállítást a látogatóknak."

    # initializing a Pinecone index
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=YOUR_ENV
    )

    index_name = "chat-doc-ts"

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

def retrieve(query_text):
    index_name = "chat-doc-ts"

    index = pinecone.Index(index_name)

    res = openai.Embedding.create(
        input=[query_text],
        engine=embed_model
    )
    # retrieve from Pinecone
    xq = res['data'][0]['embedding']

    # get relevant contexts
    # res = index.query(xq, top_k=3, include_metadata=True)
    res = index.query(xq, top_k=2, include_metadata=True)

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
        # "Egy Telekom ügyfélszolgálatos asszisztens beszélget az ügyfelekkel. Válaszolj a kérdésekre a következő context alapján. "
        "Informatika Történeti Kiállítás, számítógépmúzeum. A tárlatvezető ismerteti a kiállítást és válaszol a látogatóknak a következő context alapján. Context: "
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