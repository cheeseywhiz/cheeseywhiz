#!/home/cheese/cheeseywhiz/http/bin/python
from json.decoder import JSONDecodeError
from flask import Flask, render_template, request
from static import jsonvis

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    if 'url' in request.form:
        # data entered
        current_url = request.form['url']
        template_name = 'json.html'
        try:
            data = jsonvis.download(current_url)
        except JSONDecodeError as error:
            return render_template(
                'error.html', current_url=current_url,
                error='Either 404 or URL was not .json format',
            )
        jsonvis.make_html(data, 4, template_name=template_name)
        return render_template(template_name, current_url=current_url)
    else:
        # no data entered/opening page
        return render_template('index.html')


if __name__ == '__main__':
    app.run()
