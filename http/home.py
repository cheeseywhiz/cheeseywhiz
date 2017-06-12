"""\
execute from virtualenv:
python home.py
"""
import time
from json.decoder import JSONDecodeError
from flask import Flask, render_template, request
from static import HTTPException, JsonVis, NotFound

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True


def timer(initial):
    print('%.6f seconds to serve'%(time.clock() - initial))


@app.route('/', methods=['POST', 'GET'])
def index():
    """\
    Homepage
    """
    t0 = time.clock()
    if 'url' in request.form:
        # data entered
        current_url = request.form['url']
        try:
            instructions = JsonVis().download(current_url).make_instructions()
        except JSONDecodeError:
            raise NotFound(
                message='Site either not found or is not json format',
                current_url=current_url
            )
        file = render_template(
            'json.html', current_url=current_url, instructions=instructions
        )
        timer(t0)
        return file
    else:
        # no data entered/opening page
        file = render_template('index.html')
        timer(t0)
        return file


@app.errorhandler(HTTPException)
def handler(error):
    """\
    Handle all exceptions based from HTTPException.
    """
    return error.handle()


if __name__ == '__main__':
    app.run(host='0.0.0.0')
