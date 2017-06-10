# python home.py
from json.decoder import JSONDecodeError
from flask import Flask, render_template, request
from static.exceptions import HTTPException, NotFound
from static.jsonvis import JsonVis

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True


@app.route('/', methods=['POST', 'GET'])
def index():
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
        return render_template(
            'json.html', current_url=current_url, instructions=instructions
        )
    else:
        # no data entered/opening page
        return render_template('index.html')


@app.errorhandler(HTTPException)
def handler(error):
    return error.handle()


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        # use_reloader=True,
    )
