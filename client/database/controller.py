from sqlalchemy.exc import IntegrityError

from client.database.db_connector import DataAccessLayer
from client.database.models import Client, History


class ClientMessages:
    def __init__(self, conn_string, base, echo):
        """create connection to DB"""
        self.dal = DataAccessLayer(conn_string, base, echo=echo)
        self.dal.connect()
        self.dal.session = self.dal.Session()

    def get_client_by_username(self, username):
        """get client on DB by username"""
        return self.dal.session.query(Client).filter(Client.username == username).first()

    def add_client(self, username, password):
        """add client to DB"""
        if self.get_client_by_username(username):
            return f'Пользователь{username} уже существует.'
        else:
            new_user = Client(username=username, password=password)
            self.dal.session.add(new_user)
            self.dal.session.commit()
            print(f'Добавлен пользователь {username}.')

    def add_client_history(self, client_username, ip_addr='8.8.8.8'):
        """add client input history to BD"""
        client = self.get_client_by_username(client_username)
        if client:
            new_history = History(ip_addr=ip_addr, client_id=client.id)
            try:
                self.dal.session.add(new_history)
                self.dal.session.commit()
                print(f'Добавлена запись в историю: {new_history}')
            except IntegrityError as err:
                print(f'Ошибка интеграции с базой данных: {err}')
                self.dal.session.rollback()
        return f'Пользователь {client_username} не существует.'

    def set_user_online(self, client_username):
        """change client status by online"""
        client = self.get_client_by_username(client_username)
        if client:
            client.online_status = True
            self.dal.session.commit()
        return f'Пользователь {client_username} не существует.'
