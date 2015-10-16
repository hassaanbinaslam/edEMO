#----- Imports -----#
from flask import Flask, request, render_template
from flask.ext.bootstrap import Bootstrap

#----- App Config. -----#
app = Flask(__name__)
bootstrap = Bootstrap(app)

#----- Controllers -----#
@app.route('/index')
def index():
    return render_template('pages/index.html')

@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')

#----- Launch -----#
if __name__ == '__main__':
    #app.run(debug=True)
    app.run()