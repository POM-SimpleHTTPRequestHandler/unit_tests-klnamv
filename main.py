import json
from http.server import HTTPServer, BaseHTTPRequestHandler

USERS_LIST = [
    {
        "id": 1,
        "username": "theUser",
        "firstName": "John",
        "lastName": "James",
        "email": "john@email.com",
        "password": "12345",
    }
]


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_response(self, status_code=200, body=None):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body if body else {}).encode('utf-8'))

    def _pars_body(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        return json.loads(self.rfile.read(content_length).decode('utf-8'))  # <--- Gets the data itself

    def do_GET(self):
        global USERS_LIST
        if self.path == '/reset':
            USERS_LIST = [
                {
                    "id": 1,
                    "username": "theUser",
                    "firstName": "John",
                    "lastName": "James",
                    "email": "john@email.com",
                    "password": "12345",
                }
            ]
            self.send_response(200)
            self.send_header('', '')
            self.end_headers()
        elif self.path[:6] == '/user/':
            user_name = self.path[6:]

            users = {d['username']: d for d in USERS_LIST}
            if user_name in users:
                self.send_response(200)
                self.send_header('', '')
                self.end_headers()
                self.wfile.write(json.dumps(users[user_name]).encode(encoding='utf-8'))
            else:
                self.send_response(400, 'User not found')
                self.send_header('', '')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'User not found'}).encode(encoding='utf-8'))
        elif self.path == '/users':
            self.send_response(200)
            self.send_header('', '')
            self.end_headers()
            self.wfile.write(json.dumps(USERS_LIST).encode(encoding='utf-8'))

    def do_POST(self):
        keys = {'id', 'username', 'firstName', 'lastName', 'email', 'password'}
        if self.path == '/user/createWithList':
            new_users = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            for user in new_users:
                if user in USERS_LIST:
                    self.send_response(400)
                    self.send_header('', '')
                    self.end_headers()
                    self.wfile.write(json.dumps({}).encode(encoding='utf-8'))
                    return
            self.send_response(201)
            USERS_LIST.extend(new_users)
            self.send_header('', '')
            self.end_headers()
            self.wfile.write(json.dumps(new_users).encode(encoding='utf-8'))
        if self.path == '/user':
            new_user = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            if new_user in USERS_LIST or set(new_user.keys()) != keys:
                self.send_response(400)
                self.send_header('', '')
                self.end_headers()
                self.wfile.write(json.dumps({}).encode(encoding='utf-8'))
            else:
                self.send_response(201)
                USERS_LIST.append(new_user)
                self.send_header('', '')
                self.end_headers()
                self.wfile.write(json.dumps(new_user).encode(encoding='utf-8'))

    def do_PUT(self):
        keys = {'username', 'firstName', 'lastName', 'email', 'password'}
        if self.path[:6] == '/user/':
            try:
                id = int(self.path[6:])
            except:
                raise ValueError('id is not valid')

            update_user = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            ids = {user['id']: user for user in USERS_LIST}

            if set(update_user.keys()) != keys:
                self.send_response(400)
                self.send_header('', '')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'not valid request data'}).encode(encoding='utf-8'))
            elif id not in ids:
                self.send_response(404)
                self.send_header('', '')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'User not found'}).encode(encoding='utf-8'))
            else:
                self.send_response(200)
                old_user = ids[id]
                update_user['id'] = id
                for key in old_user.keys():
                    old_user[key] = update_user[key]
                self.send_header('', '')
                self.end_headers()
                self.wfile.write(json.dumps(old_user).encode(encoding='utf-8'))

    def do_DELETE(self):
        if self.path[:6] == '/user/':
            try:
                id = int(self.path[6:])
            except:
                raise ValueError('id is not valid')
            ids = {user['id']: user for user in USERS_LIST}
            if id not in ids:
                self.send_response(404)
                self.send_header('', '')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'User not found'}).encode(encoding='utf-8'))
            else:
                self.send_response(200)
                self.send_header('', '')
                self.end_headers()
                self.wfile.write(json.dumps({}).encode(encoding='utf-8'))


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, host='localhost', port=8000):
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
