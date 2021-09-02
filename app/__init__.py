from flask import Flask

app = Flask(__name__)

@app.route('/', methods=['GET'])
def test():
    return '<h1>the app is running</h1>'