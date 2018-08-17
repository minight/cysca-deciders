from flask import Flask, request, abort
app = Flask(__name__)
import os
import re

assert os.environ['FLAG']

INDEX = open('/app/index.html').read()

HALL_OF_SHAME = []

@app.route("/")
def hello():
    for ip in request.headers.get('X-Forwarded-For', '').split(','):
        ip = ip.strip().lower()
        if ip in HALL_OF_SHAME:
            abort(403)

    if 'f' in request.args:
        try:
            f = request.args['f']
            if re.search(r'proc|random|zero|stdout|stderr', f):
                abort(403)
            elif '\x00' in f:
                abort(404)
            return open(f).read(4096)
        except IOError:
            abort(404)
    else:
        return INDEX

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=80)

