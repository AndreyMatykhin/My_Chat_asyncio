import sys
from argparse import ArgumentParser
from asyncio import get_event_loop, set_event_loop

from PyQt5.QtWidgets import QApplication, QDialog
from quamash import QEventLoop

from client.client_config import PORT, DB_PATH
from client.ui.windows import LoginWindow, ContactsWindow
from client.utils.client_proto import ClientAuth, ChatClientProtocol


class ConsoleClientApp:
    """Console Client"""

    def __init__(self, parsed_args, db_path):
        self.args = parsed_args
        self.db_path = db_path
        self.ins = None

    def main(self):
        # create event loop
        loop = get_event_loop()
        # authentication process
        auth = ClientAuth(db_path=self.db_path)
        while True:
            usr = self.args['user'] or input('username: ')
            passwrd = self.args['password'] or input('password: ')
            auth.username = usr
            auth.password = passwrd
            is_auth = auth.authenticate()
            if is_auth:
                break
            else:
                print('wrong username/password')
        tasks = []
        client_ = ChatClientProtocol(db_path=self.db_path,
                                     loop=loop,
                                     username=usr,
                                     password=passwrd)
        try:
            coro = loop.create_connection(lambda: client_, self.args['addr'], self.args['port'])
            print(f"ох 2 - {coro}")
            transport, protocol = loop.run_until_complete(coro)
            print(f"ох 3 - {transport, protocol}")
        except ConnectionRefusedError:
            print('Error. Wrong server')
            exit(1)
        try:
            task = loop.create_task(client_.get_from_console())
            print(f"ох 4 - {task}")
            tasks.append(task)
            loop.run_until_complete(task)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)
        finally:
            loop.close()


class GuiClientApp:
    """GUI Client"""

    def __init__(self, parsed_args, db_path):
        self.args = parsed_args
        self.db_path = db_path
        self.ins = None

    def main(self):
        # client event loop
        app = QApplication(sys.argv)
        loop = QEventLoop(app)
        set_event_loop(loop)
        auth_ = ClientAuth(db_path=self.db_path)
        login_wnd = LoginWindow(auth_instance=auth_)
        if login_wnd.exec_() == QDialog.Accepted:
            client_ = ChatClientProtocol(db_path=self.db_path, loop=loop, username=login_wnd.username,
                                         password=login_wnd.password)
            wnd = ContactsWindow(client_instance=client_, user_name=login_wnd.username)
            client_.gui_instance = wnd
            with loop:
                del auth_
                del login_wnd
                try:
                    coro = loop.create_connection(lambda: client_, self.args['addr'], self.args['port'])
                    server = loop.run_until_complete(coro)
                except ConnectionRefusedError:
                    print('Error. Wrong server.')
                    exit(1)
                wnd.show()
                client_.get_from_gui()
                try:
                    loop.run_forever()
                except KeyboardInterrupt:
                    pass
                except Exception:
                    pass


def parse_and_run():
    def parse_args():
        parser = ArgumentParser(description='Client settings')
        parser.add_argument('--user', default='user1', type=str)
        parser.add_argument('--password', default='123', type=str)
        parser.add_argument('--addr', default='127.0.0.1', type=str)
        parser.add_argument('--port', default=PORT, type=int)
        parser.add_argument('--nogui', action='store_true')
        return vars(parser.parse_args())

    args = parse_args()
    if args['nogui']:
        a = ConsoleClientApp(args, DB_PATH)
        a.main()
    else:
        a = GuiClientApp(args, DB_PATH)
        a.main()


if __name__ == '__main__':
    parse_and_run()
