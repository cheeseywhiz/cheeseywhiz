from json.decoder import JSONDecodeError
from flask import Flask, render_template, request
from static.jsonvis import JsonVis

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    if 'url' in request.form:
        # data entered
        current_url = request.form['url']
        template_name = 'json.html'
        try:
            JsonVis().download(current_url).make_html(template_name, 4)
        except JSONDecodeError as error:
            return render_template(
                'error.html', current_url=current_url,
                error='Either 404 or URL was not .json format',
            )
        return render_template(template_name, current_url=current_url)
    else:
        # no data entered/opening page
        return render_template('index.html')


if __name__ == '__main__':
    app.run()
