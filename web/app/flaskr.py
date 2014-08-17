#!flask/bin/python
# all the imports
import os, subprocess, logging
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask.sessions import SessionInterface
logging.basicConfig(filename='example.log',level=logging.DEBUG,format='%(asctime)s %(message)s')
# create our little application :)
app = Flask(__name__)
app.secret_key = '\x16\x14\x19XO\xac\xeb\xfbfb\xb5+\xf9\xe1h\xe7\x9d\x83\x8c\xf5W\xff\x03'

@app.route('/')
def home():
    return redirect(url_for('index'))
@app.route('/index',methods=['GET','POST'])
def index():
    error = None
    return render_template('main.html',method=['POST'])
@app.route('/action',methods=['GET','POST'])
def action():
    i = request.form['button']
    if(i=='Start'):
        lightsOn()
        return redirect(url_for('back'))
    elif(i=='Animation'):
        return redirect(url_for('back'))
    elif(i=='Stop'):
        lightsOff()
        return redirect(url_for('back'))
    elif(i =='Back'):
        return redirect(url_for('index'))
    return redirect(url_for('back'))    

@app.route('/back',methods=['GET','POST'])
def back():
    message = 'message'
    return render_template('back.html',method=['POST'])
def lightsOn():
    cmd = ["supervisorctl","start","PyLights"]
    ls_output = subprocess.check_output(cmd)

def lightsOff():
    cmd = ["supervisorctl","stop","PyLights"]
    ls_output = subprocess.check_output(cmd)
    cmd2 = ["supervisorctl","start","LightsOff"]
    ls_output2 = subprocess.check_output(cmd2)


def runSequence(sequenceName):
    cmd = ["screen","-r","-S","screename","command"]
    ls_output = subprocess.check_output(cmd)

if __name__ == '__main__':
    app.run(host = "0.0.0.0",port = 80,debug =True)
