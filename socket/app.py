"""A sample custom HTTP server."""
import functools
import html
import traceback

import server

HTML_TMPL = '''\
<html>
<head>
    <link rel="stylesheet" type="text/css" href="/myStyle.css"/>
</head>
<body id="consolas">
%s
</body>
</html>
'''

app = server.app.App('0.0.0.0', 8080)
server.http.HTTPPath.root = __file__ + '/..'
app.register_filesystem({
    'img.png': '~/Pictures/wallpapers/tikkle7e9qhz.jpg',
    'myStyle.css': 'myStyle.css',
    'pkg': 'server',
    'root': '/',
    'imgs': '~/Pictures/',
    'imgs/wallpapers': '~/Pictures/wallpapers',
})


def insert_body(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return HTML_TMPL % func(*args, **kwargs)

    return wrapper


@app.register('/')
@insert_body
def index(req):
    return '''\
    <a href="/img.png"><img src="/img.png" width="250"/></a>
    <form action="/" method="post">
        <input id="consolas" type="text" name="url"><br/>
        <input id="consolas" type="submit" value="Submit">
    </form>'''


@insert_body
def dir_landing_page(uri_path, folder_path, req):
    return (
        f'    <h1>{uri_path}</h1>'
        + '<br/>'.join(
            '\n    <a href="%s">%s</a>' % (
                server.http.HTTPPath(uri_path / file.relpath(folder_path)).url,
                file.relpath(folder_path))
            for file in folder_path
            # if file.is_file()
        )
    )


for uri_path, (fs_path, _) in app.registered_folders.items():
    app.register(uri_path)(
        functools.partial(dir_landing_page, uri_path, fs_path)
    )


@app.register('/', 'post')
@insert_body
def index_post(req):
    input = req.body['url']
    return f'''
    <p>
        {input}<br/>
        <a href="/">Home</a>
    </p>
'''


@app.register('page')
def page(req):
    return 307, {'Location': '/new'}, HTML_TMPL % ''


@app.register('new')
@insert_body
def new(req):
    return '<p>This is the new page. You may have been redirected.</p>'


@app.register_exception(server.http.HTTPException)
def handle_http(error):
    body = '''\
    <h1>%d %s</h1>
    <pre id="consolas">%s</pre>
''' % (error.status_code, error.reason, html.escape(error.message))

    return error.status_code, HTML_TMPL % body


@app.register_exception(Exception)
def handle_exc(error):
    new_error = server.http.HTTPException(traceback.format_exc(), 500)
    return handle_http(new_error)


if __name__ == '__main__':
    app.run()
