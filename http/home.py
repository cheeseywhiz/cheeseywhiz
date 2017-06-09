# export FLASK_APP=home.py
# flask run --host=0.0.0.0
import re
from json.decoder import JSONDecodeError
from flask import Flask, render_template, request
from static.jsonvis import JsonVis

app = Flask(__name__)


class HTTPException(Exception):
    def __init_subclass__(cls, status_code):
        super().__init_subclass__()
        cls.status_code = status_code
        words = re.findall('[A-Z][^A-Z]*', cls.__name__)
        cls.type = ' '.join(words)


class NotFound(HTTPException, status_code=404):
    def __init__(self, message, current_url):
        self.message = message
        self.current_url = current_url


@app.route('/', methods=['POST', 'GET'])
def index():
    if 'url' in request.form:
        # data entered
        current_url = request.form['url']
        template_name = 'json.html'
        try:
            JsonVis().download(current_url).make_html(template_name, 4)
        except JSONDecodeError:
            raise NotFound(
                'Site either not found or is not json format',
                current_url=current_url
            )
        return render_template(template_name, current_url=current_url)
    else:
        # no data entered/opening page
        return render_template('index.html')


@app.errorhandler(NotFound)
def error(error):
    return render_template(
        'error.html', current_url=error.current_url, error=error
    ), 404
