#----- Imports -----#
from flask import Flask, request, render_template
from flask.ext.bootstrap import Bootstrap

#----- App Config. -----#
app = Flask(__name__)
bootstrap = Bootstrap(app)

#----- Controllers -----#
@app.route('/')
def home():
    return render_template('pages/home.html')

@app.route('/login')
def login():
    return render_template('pages/login.html')

@app.route('/profile')
def profile():
    return render_template('pages/view-profile.html')

#----- Launch -----#
if __name__ == '__main__':
    #app.run(debug=True)
    app.run()