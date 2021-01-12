from flask import Flask, request, jsonify, json, abort, redirect, url_for, render_template
from flask_cors import CORS, cross_origin
import os
import shutil
import re
import subprocess
import traceback
import docker
import re
import json

app = Flask(__name__, template_folder='template')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

catfile = "catalog.json"
catalog = []
if os.path.exists(catfile):
    with open(catfile) as f:
        catalog = json.load(f)

@app.route('/test', methods=['GET', 'POST'])
@cross_origin()
def r_test():
    data = clist() 
    return jsonify(data)

@app.route('/', methods=['GET', 'POST'])
@cross_origin()
def main():

    return render_template("index.html", containers=clist(), url="http://codeserver")

@app.route('/delete/<cname>', methods=['GET', 'POST'])
@cross_origin()
def r_delete(cname):
    #codeserver_vuejs-materialize-boilerplate_dp8455_lp8092_bp9102
    folder = cname.split("_dp")[0].strip()
    filepath = f"/root/{folder}"
    c = os.system(f"docker rm -f {cname}")
    if c == 0:
        if folder != "" and "codeserver_" in folder:
            if os.path.exists(filepath):
                print(f"delete {filepath}")
                shutil.rmtree(filepath)
    return redirect(url_for("main"))

@app.route('/reset/<cname>', methods=['GET', 'POST'])
@cross_origin()
def r_reset(cname):
    cmd = gen_cmd(parse_cname(cname))
    os.system(cmd)
    return redirect(url_for("main"))

@app.route('/restart/<label>', methods=['GET', 'POST'])
@cross_origin()
def r_restart(label):
    os.system(f"docker restart {label}")
    return redirect(url_for("main"))

@app.route('/start/<label>', methods=['GET', 'POST'])
@cross_origin()
def r_start(label):
    os.system(f"docker start {label}")
    return redirect(url_for("main"))

@app.route('/stop/<label>', methods=['GET', 'POST'])
@cross_origin()
def r_stop(label):
    os.system(f"docker stop {label}")
    return redirect(url_for("main"))

@app.route('/create/<label>', methods=['GET', 'POST'])
@cross_origin()
def add(label):
    
    print(label)
    create_container(label)

    return redirect(url_for("main"))

def parse_cname(cname):
    ret = {}
    m = re.search("([^_]+)_dp(\d+)_lp(\d+)_bp(\d+)", cname)
    if m:
        g = m.groups()
        ret = {v:int(g[k]) if k > 0 else g[k] for k,v in enumerate(["name", "dp", "lp", "bp"])}
        ret["label"] = ret["name"]

    return ret

def clist():
    client = docker.from_env()
    ret = []
    for container in client.containers.list(all=True):
        cname = container.name
        p = parse_cname(cname)
        if p:
            ret.append({
                **p,
                "status": container.status,
                "status_html": render_status_html(container.status),
                "cname": container.name,
                "cmd": gen_cmd(p)
            })

    return ret 

def render_status_html(status):
    if status == "exited":
        return f"<img src='https://cdn3.iconfinder.com/data/icons/fatcow/32/bullet_red.png'/>"
    elif status == "running": 
        return f"<img src='https://cdn3.iconfinder.com/data/icons/fatcow/32/bullet_green.png'/>"

    return status

def gen_cmd(params):
    cmd = """
args="{label}:{dp}:{lp}:{bp}"
codeserver_name=$( echo $args | cut -d: -f1)
codeserver_ide=$( echo $args | cut -d: -f2)
codeserver_live=$( echo $args | cut -d: -f3)
codeserver_back=$( echo $args | cut -d: -f4)
codeserver_label="${{codeserver_name}}_dp${{codeserver_ide}}_lp${{codeserver_live}}_bp${{codeserver_back}}"
label="codeserver_${{codeserver_name}}"
dlabel="codeserver_${{codeserver_label}}"
folder="/root/$label"
[ ! -d $folder ] && mkdir $folder 
chmod -R 777 $folder
docker rm -f $dlabel
docker run -dit --name $dlabel \
    --restart unless-stopped \
    --cap-add SYS_ADMIN --device /dev/fuse \
    -e SERVICE_URL=https://extensions.coder.com/api \
    -p $codeserver_ide:8443 \
    -p $codeserver_live:8080 \
    -p $codeserver_back:9090 \
    -v $folder:/home/coder/project \
    crashlaker/mycodeserver:v1
    """.format(**params)

    return cmd

def create_container(label):
    cs = clist()
    if len(cs) == 0:
        dp = 8443
        lp = 8080
        bp = 9090
    else:
        dp = max([c["dp"] for c in cs])+1
        lp = max([c["lp"] for c in cs])+1
        bp = max([c["bp"] for c in cs])+1

    p = {
        "label": label,
        "dp": dp,
        "lp": lp,
        "bp": bp
    }
    cmd = gen_cmd(p)
    os.system(cmd)


# gunicorn --workers=2 'app:create_app()' --bind=0.0.0.0:<port>
def create_app():
    return app

if __name__ == '__main__':
    #foo()
    #print(clist())
    #create_container()
    app.run(host='0.0.0.0', port=80)
    
    #test 
    #with app.test_client() as c:
    #    rs = c.get("/")
    #    print(rs.data)

