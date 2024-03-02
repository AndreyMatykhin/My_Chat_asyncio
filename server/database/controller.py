from datetime import datetime

from sqlalchemy.exc import IntegrityError

from server.database.db_connector import DataAccessLayer
from server.database.models import Client, History, Contacts, Messages


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

    def add_contact(self, client_username, contact_username):
        """add contact"""
        contact = self.get_client_by_username(contact_username)
        if contact:
            client = self.get_client_by_username(client_username)
            if client:
                new_contact = Contacts(client_id=client.id, contact_id=contact.id)
                try:
                    self.dal.session.add(new_contact)
                    self.dal.session.commit()
                    print(f'Contact added: {new_contact}')
                except IntegrityError as err:
                    print(f'IntegrityError: {err}')
                    self.dal.session.rollback()
            else:
                return f'Client {client_username} does not exists.'
        else:
            return f'Contact {contact_username} does not exists.'

    def del_contact(self, client_username, contact_username):
        """delete contact"""
        contact = self.get_client_by_username(contact_username)
        if contact:
            client = self.get_client_by_username(client_username)
            if client:
                remove_contact = self.dal.session.query(Contacts).filter(
                    (Contacts.contact_id == contact.id) & (Contacts.client_id == client.id)).first()
                if remove_contact:
                    self.dal.session.delete(remove_contact)
                    self.dal.session.commit()
                    print(f'Contact removed: {remove_contact}')
                else:
                    return f'{contact_username} is not contact (friend) of {client_username}'
            else:
                return f'Client {client_username} does not exists.'
        else:
            return f'Contact {contact_username} does not exists.'

    def get_contacts(self, client_username):
        """get contacts by client"""
        client = self.get_client_by_username(client_username)
        if client:
            return (self.dal.session.query(Contacts).join(Client, Contacts.client_id == client.id).filter(
                Client.username == client_username).all())
        return f'Client {client_username} does not exists.'

    def get_all_clients(self):
        """get all register client"""
        return self.dal.session.query(Client).all()

    def get_client_history(self, client_username):
        """get history by client"""
        client = self.get_client_by_username(client_username)
        if client:
            return self.dal.session.query(History).filter(History.client_id == client.id).all()
        return f'Client {client_username} does not exists.'

    def set_user_offline(self, client_username):
        """set status to offline
        :param client_username:
        :return:"""
        client = self.get_client_by_username(client_username)
        if client:
            client.online_status = False
            self.dal.session.commit()
        else:
            return f'Client {client_username} does not exists.'

    def get_user_status(self, client_username):
        client = self.get_client_by_username(client_username)
        if client:
            return client.online_status
        else:
            return f'Client {client_username} does not exists.'

    def add_client_message(self, client_username, contact_username, text_msg):
        """add and backupp cliwnt massage"""
        client = self.get_client_by_username(client_username)
        contact = self.get_client_by_username(contact_username)
        if client and contact:
            new_msg = Messages(client_id=client.id, contact_id=contact.id, message=text_msg, time=datetime.now())
            try:
                self.dal.session.add(new_msg)
                self.dal.session.commit()
                print(f'New message added: {new_msg}')
            except IntegrityError as err:
                print(f'IntgrityError error : {err}')
                self.dal.session.rollback()
        print(f'Client {client_username} does not exists.')

    def get_client_messages(self, client_username):
        """get all messages by client"""
        client = self.get_client_by_username(client_username)
        if client:
            return self.dal.session.query(Messages).filter(Messages.client_id == client.id).all()
        return f'Client {client_username} does not exists.'
