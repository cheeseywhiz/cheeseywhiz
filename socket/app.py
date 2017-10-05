import traceback
import apputil
import httputil

app = apputil.App('0.0.0.0', 8080)


@app.register('/')
def index(req):
    return '''\
<form action="/" method="post">
    <input id="text" type="text" name="url"><br/>
    <input type="submit" value="Submit">
</form>
'''


@app.register('/', 'post')
def index_post(req):
    input = req.body['url']
    return f'<p>{input}</p>'


@app.register('/page')
def page(req):
    return 308, {'Location': '/new'}, ''


@app.register('/new')
def new(req):
    return '<p>This is the new page. You may have been redirected.</p>'


@app.handle_exc(httputil.HTTPException)
def handle_http(error):
    return error.status_code, error.format()


@app.handle_exc(Exception)
def handle_exc(error):
    new_error = httputil.HTTPException(traceback.format_exc(), 500)
    return handle_http(new_error)


if __name__ == '__main__':
    app.run()
