from flask import Flask
from flask import request
from flask import render_template
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route('/')
def index():
    return render_template('pages/index.html')


if __name__ == '__main__':
    app.run()