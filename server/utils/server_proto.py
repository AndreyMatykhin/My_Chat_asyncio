from asyncio import Protocol
from binascii import hexlify
from functools import wraps
from hashlib import pbkdf2_hmac

from server.utils.mixins import ConvertMixin, DbInterfaceMixin
from server.utils.server_messages import JimServerMessage


class ChatServerProtocol(Protocol, ConvertMixin, DbInterfaceMixin):
    def __init__(self, db_path, connections, users):
        """A Server Protocol listening for subscriber messages """
        super().__init__(db_path)
        self.connections = connections
        self.users = users
        self.jim = JimServerMessage()
        # useful temp variables
        self.user = None
        self.transport = None

    def eof_received(self):
        self.transport.close()

    def connection_made(self, transport):
        """ Called when connection is initiated """
        self.connections[transport] = {
            'peername': transport.get_extra_info('peername'),
            'username': '',
            'transport': transport
        }
        self.transport = transport

    def connection_lost(self, exc):
        if isinstance(exc, ConnectionResetError):
            print('ConnectionResetError')
            print(self.connections)
            print(self.users)
        # remove closed connections
        rm_con = []
        for con in self.connections:
            if con._closing:
                rm_con.append(con)
        for i in rm_con:
            del self.connections[i]
        # remove from users
        rm_users = []
        for k, v in self.users.items():
            for con in rm_con:
                if v['transport'] == con:
                    rm_users.append(k)
        for u in rm_users:
            del self.users[u]
            self.set_user_offline(u)
            print(f'{u} disconnected')

    def authenticate(self, username, password):
        # check user in DB
        if username and password:
            usr = self.get_client_by_username(username)
            hashed_password = hexlify(pbkdf2_hmac('sha256', password.encode('utf-8'), 'salt'.encode('utf-8'), 100000))
            if usr:
                # existing user
                if hashed_password == usr.password:
                    # add client's history row
                    self.add_client_history(username)
                    return True
                else:
                    return False
            else:
                # new user
                print('new user')
                self.add_client(username, hashed_password)

                self.add_client_history(username)
                return True
        else:
            return False

    def _login_required(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            is_auth = self.get_user_status(self.user)
            if is_auth:
                result = func(self, *args, **kwargs)
                return result
            else:
                resp_msg = self.jim.responce(code=501, error='login required')
                self.users[self.user]['transport'].write(self._dict_to_bytes(resp_msg))
        return wrapper

    @_login_required
    def action_msg(self, data):
        try:
            if data['from']:  # send msg to sender's chat
                print(data)
                # save msg to DB history message
                self._cm.add_client_message(data['from'], data['to'], data['message'])
                self.users[data['from']]['transport'].write(self._dict_to_bytes(data))
            if data['to'] and data['from'] != data['to']:
                try:
                    self.users[data['to']]['transport'].write(self._dict_to_bytes(data))
                except KeyError:
                    print(f'{data["to"]} is connected yet.')
        except Exception as er:
            resp_msg = self.jim.responce(code=500, error=er)
            self.transport.write(self._dict_to_bytes(resp_msg))

    def data_received(self, data):
        _data = self._bytes_to_dict(data)
        if data:
            try:
                if _data['action'] == 'presence':
                    if _data['user']['account_name']:
                        resp_msg = self.jim.response(code=200)
                        self.transport.write(self._dict_to_bytes(resp_msg))
                    else:
                        resp_msg = self.jim.response(code=500, error='wrong presence message')
                        self.transport.write(self._dict_to_bytes(resp_msg))
                elif _data['action'] == 'msg':
                    self.user = _data['from']
                    self.action_msg(_data)
                elif _data['action'] == 'authenticate':
                    if self.authenticate(_data['user']['account_name'],
                                         _data['user']['password']):
                        if _data['user']['account_name'] not in self.users:
                            self.user = _data['user']['account_name']
                            self.connections[self.transport]['username'] = self.user
                            self.users[_data['user']['account_name']] = self.connections[self.transport]
                            self.set_user_online(_data['user']['account_name'])
                        resp_msg = self.jim.probe(self.user)
                        self.users[_data['user']['account_name']]['transport'].write(self._dict_to_bytes(resp_msg))
                    else:
                        resp_msg = self.jim.response(code=402, error='wrong login/password')
                        self.transport.write(self._dict_to_bytes(resp_msg))
            except Exception as e:
                resp_msg = self.jim.response(code=500, error=e)
                self.transport.write(self._dict_to_bytes(resp_msg))
        else:
            resp_msg = self.jim.response(code=500, error='you sent a message without a name or data.')
            self.transport.write(self._dict_to_bytes(resp_msg))
