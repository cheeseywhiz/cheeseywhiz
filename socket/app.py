"""A sample custom HTTP server."""
import functools
import html
import traceback

import server

server.Logger.name = __file__
HTML_TMPL = '''\
<html>
<head>
    <link rel="stylesheet" type="text/css" href="/myStyle.css"/>
</head>
<body id="consolas">
%s</body>
</html>
'''
LINK_HOME = '<a href="/">Home</a>'

app = server.app.App('0.0.0.0', 8080)
server.http.Path.root = ''
app.register_filesystem({
    'img.png': '~/Pictures/wallpapers/tikkle7e9qhz.jpg',
    'myStyle.css': 'myStyle.css',
    'pkg': 'server',
    'home': ('~', False),
    'imgs': '~/Pictures/',
})


def insert_body(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)

        if isinstance(response, tuple):
            status_code, headers, text = response
            return status_code, headers, HTML_TMPL % text
        else:
            return HTML_TMPL % response

    return wrapper


@app.register('/')
@insert_body
def index(req):
    return '''\
    <a href="/img.png"><img src="/img.png" width="250"/></a>
    <form action="/" method="post">
        <input id="consolas" type="text" name="url"><br/>
        <input id="consolas" type="submit" value="Submit">
    </form>
'''


@insert_body
def dir_landing_page(uri_path, folder_path, recursive, req):
    def contents():
        yield folder_path.parent
        yield folder_path
        yield from folder_path

    parts = []

    for file in contents():
        rel_path = file.relpath(folder_path)
        new_uri = uri_path / rel_path
        if recursive or file.is_file():
            parts.append(f'''
        <a href="{new_uri}">{rel_path}</a>''')

    inner = '<br/>'.join(parts)
    return f'''\
    <h1>{LINK_HOME}{uri_path}</h1>
    <p>{inner}
    </p>
'''


for uri_path, fs_path in app.registered_fs_paths.items():
    if isinstance(fs_path, tuple):
        fs_path, recursive = fs_path
    else:
        recursive = True

    if not fs_path.is_dir():
        continue

    def contents():
        if recursive:
            yield from fs_path.tree
        else:
            yield fs_path

    for file in contents():
        if not file.is_dir():
            continue

        rel_file = file.relpath(fs_path)
        new_uri = uri_path / rel_file
        app.register(new_uri)(
            functools.partial(dir_landing_page, new_uri, file, recursive)
        )


@app.register('/', 'post')
def index_post(req):
    input = req.body['url']
    new_uri = server.http.Path(input)
    return 303, {'Location': str(new_uri)}, ''


@app.register('page')
def page(req):
    return 307, {'Location': '/new'}, ''


@app.register('new')
@insert_body
def new(req):
    return f'''\
    <p>
        This is the new page. You may have been redirected.<br/>
        {LINK_HOME}
    </p>
'''


@app.register_exception(server.http.HTTPException)
def handle_http(error):
    body = f'''\
    <h1>{error.status_code} {error.reason}</h1>
    <pre id="consolas">{html.escape(str(error.message))}</pre>
    {LINK_HOME}
'''

    return error.status_code, HTML_TMPL % body


@app.register_exception(Exception)
def handle_exc(error):
    new_error = server.http.HTTPException(traceback.format_exc(), 500)
    return handle_http(new_error)


print('ready')

if __name__ == '__main__':
    app.run()
