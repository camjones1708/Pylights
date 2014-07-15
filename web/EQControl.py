from flask import Flask
import subprocess

app = Flask(__name__)

@app.route("/")
def index():
    return ()

def lightsOn():
	cmd = ["supervisorctl","start","eq"]
	ls_output = subprocess.check_output(cmd)

def lightsOff():
	cmd = ["supervisorctl","stop","eq"]
	ls_output = subprocess.check_output(cmd)

def runSequence(sequenceName):
	cmd = ["screen","-r","-S","screename","command"]
	ls_output = subprocess.check_output(cmd)

if __name__ == "__main__" :
    app.run(debug=True)