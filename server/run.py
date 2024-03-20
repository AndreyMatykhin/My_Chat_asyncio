from argparse import ArgumentParser
from asyncio import get_event_loop, set_event_loop
from sys import argv

from quamash import QEventLoop
from PyQt5.QtWidgets import QApplication

from server.server_config import PORT, DB_PATH
from server.ui.windows import ServerMonitorWindow
from server.utils.server_proto import ChatServerProtocol


class ConsoleServerApp:
    """Console server"""

    def __init__(self, parsed_args, db_path):
        self.args = parsed_args
        self.db_path = db_path
        self.ins = None

    def main(self):
        connections = dict()
        users = dict()
        loop = get_event_loop()
        # Each client will create a new protocol instance
        self.ins = ChatServerProtocol(self.db_path, connections, users)
        coro = loop.create_server(lambda: self.ins, self.args['addr'], self.args['port'])
        server = loop.run_until_complete(coro)
        # Serve requests until Ctrl+C
        print(f'Server on {server.sockets[0]}')
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


class GuiServerApp:
    """GUI server"""

    def __init__(self, parser_args, db_path):
        self.args = parser_args
        self.db_path = db_path
        self.ins = None

    def main(self):
        connections = dict()
        users = dict()
        # Each client will create a new protocol instance
        self.ins = ChatServerProtocol(self.db_path, connections, users)
        app = QApplication(argv)
        loop = QEventLoop(app)
        set_event_loop(loop)  # NEW must set the event loop
        # server_instance=self.ins, parsed_args=self.args
        wnd = ServerMonitorWindow(server_instance=self.ins, parsed_args=self.args)
        wnd.show()
        with loop:
            coro = loop.create_server(lambda: self.ins, self.args['addr'], self.args['port'])
            server = loop.run_until_complete(coro)
            print('Server on {} : {}'.format(*server.sockets[0].getsockname()))
            try:
                loop.run_forever()
            except KeyboardInterrupt:
                pass
            server.close()
            loop.run_until_complete(server.wait_closed())
            loop.close()


def parse_and_run():
    def parse_args():
        parser = ArgumentParser(description='Server settings')
        parser.add_argument('--addr', default='127.0.0.1', type=str)
        parser.add_argument('--port', default=PORT, type=int)
        parser.add_argument('--nogui', action='store_true')
        return vars(parser.parse_args())

    args = parse_args()
    if args['nogui']:
        # start consoles server
        print(DB_PATH)
        a = ConsoleServerApp(args, DB_PATH)
        a.main()
    else:
        a = GuiServerApp(args, DB_PATH)
        a.main()


if __name__ == '__main__':
    parse_and_run()
