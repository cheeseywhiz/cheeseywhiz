"""A sample custom HTTP server."""
import html
import traceback

import server

HTML_TMPL = '''\
<html>
<head>
    <link rel="stylesheet" type="text/css" href="myStyle.css"/>
</head>
<body id="consolas">%s</body>
</html>
'''

app = server.app.App('0.0.0.0', 8080)
server.http.HTTPPath.root = __file__ + '/..'
app.register_files({
    'img.png': '~/Pictures/wallpapers/tikkle7e9qhz.jpg',
    'myStyle.css': 'myStyle.css'
})


@app.register('/')
def index(req):
    return HTML_TMPL % '''
    <img src="img.png" width="250"/>
    <form action="/" method="post">
        <input id="consolas" type="text" name="url"><br/>
        <input id="consolas" type="submit" value="Submit">
    </form>
'''


@app.register('/', 'post')
def index_post(req):
    input = req.body['url']
    return HTML_TMPL % f'''
    <p>
        {input}<br/>
        <a href="/">Home</a>
    </p>
'''


@app.register('/page')
def page(req):
    return 307, {'Location': '/new'}, HTML_TMPL % ''


@app.register('/new')
def new(req):
    return (
        HTML_TMPL
        % '<p>This is the new page. You may have been redirected.</p>')


@app.register_exception(server.http.HTTPException)
def handle_http(error):
    body = '''\
    <h1>%d %s</h1>
    <pre>%s</pre>
''' % (error.status_code, error.reason, html.escape(error.message))

    return error.status_code, HTML_TMPL % body


@app.register_exception(Exception)
def handle_exc(error):
    new_error = server.http.HTTPException(traceback.format_exc(), 500)
    return handle_http(new_error)


if __name__ == '__main__':
    app.run()
