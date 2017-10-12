"""A sample custom HTTP server."""
import functools
import html
import traceback

import collect

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
app.resolver.update({
    '/img.png': '~/Pictures/wallpapers/tikkle7e9qhz.jpg',
    '/myStyle.css': 'myStyle.css',
    '/pkg': 'server',
    '/home': ('~', False),
    '/imgs': '~/Pictures/',
    '/cfg': '~/.config',
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
def index():
    return '''\
    <a href="/img.png"><img src="/img.png" width="250"/></a>
    <form action="/" method="post">
        <input id="consolas" type="text" name="url"><br/>
        <input id="consolas" type="submit" value="Submit">
    </form>
'''


@insert_body
def dir_landing_page(url_path, folder_path, recursive):
    def contents():
        yield folder_path.parent
        yield folder_path
        yield from folder_path

    parts = []

    for file in contents():
        rel_path = file.relpath(folder_path)
        new_url = url_path / rel_path
        if recursive or file.is_file():
            parts.append(f'''
        <a href="{new_url}">{rel_path}</a>''')

    inner = '<br/>'.join(parts)
    return f'''\
    <h1>{LINK_HOME}{url_path}</h1>
    <p>{inner}
    </p>
'''


for url_path, fs_path in app.resolver.dirs.items():
    recursive = app.resolver.recursive(fs_path)

    def contents():
        if recursive:
            yield from fs_path.tree
        else:
            yield fs_path

    for file in contents():
        if not file.is_dir():
            continue

        rel_file = file.relpath(fs_path)
        new_url = url_path / rel_file
        app.register(new_url)(
            functools.partial(dir_landing_page, new_url, file, recursive)
        )


@app.register('/', 'post')
def index_post():
    input = server.app.ActiveRequest.body['url']
    new_url = collect.path.Path(input)
    return 303, {'Location': str(new_url)}, ''


@app.register('/page')
def page():
    return 307, {'Location': '/new'}, ''


@app.register('/new')
@insert_body
def new():
    return f'''\
    <p>
        This is the new page. You may have been redirected.<br/>
        {LINK_HOME}
    </p>
'''


@app.register('/req', 'GET', 'POST')
def req_():
    return (
        200, {'Content-Type': 'text/plain'},
        server.app.ActiveRequest.raw_request)


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
