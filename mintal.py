"""
working with DRF application 'rental'
"""

import abc
import json
import requests
from requests.exceptions import HTTPError

BASE_URL = 'http://localhost:8000/api/'

URLS = {
    'friends': 'v1/friends/',
    'belongings': 'v1/belongings/',
    'borrowings': 'v1/borrowings/',
    }

class Thing(metaclass=abc.ABCMeta):
    def __init__(self, user, name=''):
        self._id = 0
        self._user = user
        self._name = name

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id_number):
        if isinstance(id_number, int):
            if id_number > 0:
                self._id = id_number
        else:
            raise TypeError("the argument 'id' should be positive integer")
        
    @property
    def name(self):
        return self._name

    @abc.abstractmethod
    def load_data(self, data):
        """
        load data from database into object
        """
        pass        


class Friend(Thing):
    """
    user's friend class
    """
    def __init__(self, user, name=''):
        super().__init__(user, name)
        self._overdue = False

    def load_data(self, data):
        self._user._load_friend_data(self, data)

    @property
    def overdue(self):
        return self._overdue

    @overdue.setter
    def overdue(self, has_overdue):
        if isinstance(has_overdue, bool):
            self._overdue = has_overdue
        else:
            bool_overdue = bool(has_overdue)
            self._overdue = bool_overdue
        
    def __str__(self):
        return f'Friend: {self._name}'

    def __repr__(self):
        return f'<Friend object: Friend.name = {self._name}>'


class Belonging(Thing):
    """
    user's belonging class
    """
    def __init__(self, user, name=''):
        super().__init__(user, name)
        self._borrowed = False

    def load_data(self, data):
        self._user._load_belonging_data(self, data)

    @property
    def borrowed(self):
        return self._borrowed

    @borrowed.setter
    def borrowed(self, is_borrowed):
        if isinstance(is_borrowed, bool):
            self._borrowed = is_borrowed
        else:
            bool_borrowed = bool(is_borrowed)
            self._borrowed = bool_borrowed
    
    def __str__(self):
        return f'Benloning: {self._name}'

    def __repr__(self):
        return f'<Belonging object: Belonging.name = {self._name}>'


class Borrow():
    """
    user's borrow class
    """
    def __init__(self, id, when, what, who, returned):
        self._id = id
        self._when = when
        self._what = what
        self._who = who
        self._returned = returned

    @property
    def id(self):
        return self._id


class User():
    """
    user class for working with 'rental'
    """
        
    def __init__(self, username):
        self._username = username
        self._friends = {}
        self._belongings = {}
        self._token = None

    def login(self, password):
        """
        get token
        """
        url = BASE_URL + 'auth/token/login/'
        data = {
            'username': self._username,
            'password': password,
            }
        reply = self._get_data_post(url, data)
        if reply:
            self._token = reply['auth_token']
            return self._token

    def logout(self):
        """
        user logout
        """
        pass

    def register(self, password):
        """
        register new user
        """
        url = BASE_URL + 'auth/users/'
        data = {
            'username': self._username,
            'password': password
            }
        reply = self._get_data_post(url, data)
        if reply:
            self._id = int(reply['id'])
            return self._id

    def _load_friend_data(self, friend, data):
        """
        load data into concreate friend object
        """
        friend.id = data['id']
        friend.overdue = bool(data['has_overdue'])
        friend._name = data['name']

    def _load_belonging_data(self, belonging, data):
        """
        load data into concreate belonging object
        """
        belonging.id = data['id']
        belonging._name = data['name']
        if 'is_borrowed' in data:
            belonging.borrowed = data['is_borrowed']

    def _add_thing(self, url, thing):
        """
        add thing object (friend, belonging)
        """
        data = {'name': thing.name}
        reply = self._get_data_post(url, data)
        if reply:
            thing.load_data(reply)
            return thing

    def _get_all_things(self, url, package, thing):
        """
        get a list of Thing (friend, belonging)
        url : API request
        collection : dict of objects of things
        thing : str name of object (friend, belonging)
        """
        while url:
            response = self._get_data_get(url)
            reply = response.json()
            if reply:
                for data in reply:
                    if thing.lower() == 'friend':
                        thing_object = Friend(self)
                    elif thing.lower() == 'belonging':
                        thing_object = Belonging(self)
                    # TODO: ValueError
                    thing_object.load_data(data)
                    package[thing_object.id] = thing_object
            url = ''
            links = response.links
            if links:
                if 'next' in links:
                    url = links['next']['url']
        return reply

    def _get_page_things(self, url, package, thing):
        """
        get a list of Thing (friend, belonging) and a links
        """
        response = self._get_data_get(url)
        reply = response.json()
        if reply:
            things = []
            for data in reply:
                if thing.lower() == 'friend':
                    thing_object = Friend(self)
                elif thing.lower() == 'belonging':
                    thing_object = Belonging(self)
                thing_object.load_data(data)
                if not thing_object.id in package:
                    package[thing_object.id] = thing_object
                things.append(thing_object)
            return things, response.links

    # workign with friends
    def get_friends(self):
        """
        get a friends list
        """
        url = BASE_URL + URLS['friends']
        response = self._get_data_get(url)
        reply = response.json()
        if reply:
            for data in reply:
                friend = Friend(self)
                friend.load_data(data)
                self._friends[friend.id] = friend
        return self._friends

    def get_all_friends(self):
        """
        get a friends list
        """
        url = BASE_URL + URLS['friends']
        self._get_all_things(url, self._friends, 'friend')

    def get_page_friends(self, page_url=''):
        """
        get only one page with friends list & links to over pages:
        first, prev, next, last - if they exists
        """
        if page_url:
            url = page_url
        else:
            url = BASE_URL + URLS['friends']
        return self._get_page_things(url, self._friends, 'friend')

    def number_friends(self):
        """
        get quantity of friends
        """
        return len(self._friends)

    def add_friend(self, friend):
        """
        add new friend
        """
        is_friend_object = False
        url = BASE_URL + URLS['friends']
        if isinstance(friend, Friend):
            pass
        elif isinstance(friend, str):
            friend = Friend(self, friend)
        else:
            return None
        friend = self._add_thing(url, friend)
        if friend:
            self._friends[friend.id] = friend
            return friend

    def friend_by_id(self, friend_id):
        """
        get friend from list by friend_id
        """
        if friend_id in self._friends:
            return self._friends[friend_id]
        
    # working with belongings
    def get_belongings(self):
        """
        get a belongings list
        """
        url = BASE_URL + URLS['belongings']
        reply = self._get_data_get(url)
        if reply:
            for data in reply:
                belonging = Belonging(self)
                belonging.load_data(data)
                self._belongings[belonging._id] = belonging
        return reply

    def get_all_belongings(self):
        """
        get a belongings list
        """
        url = BASE_URL + URLS['belongings']
        self._get_all_things(url, self._belongings, 'belonging')

    def get_page_belongings(self, page_url=''):
        """
        get only one page with belongings list & links to over pages:
        first, prev, next, last - if they exists
        """
        if page_url:
            url = page_url
        else:
            url = BASE_URL + URLS['belongings']
        return self._get_page_things(url, self._belongings, 'belonging')

    def number_belongings(self):
        """
        get quantity of belongings
        """
        return len(self._belongings)

    def belonging_by_id(self, belonging_id):
        """
        get belonging from list by belonging_id
        """
        if belonging_id in self._belongings:
            return self._belongings[belonging_id]

    def add_belonging(self, belonging):
        """
        add new belonging
        """
        url = BASE_URL + URLS['belongings']
        if isinstance(belonging, Belonging):
            pass
        elif isinstance(belonging, str):
            belonging = Belonging(self, belonging)
        else:
            return None
        belonging = self._add_thing(url, belonging)
        if belonging:
            self._belongings[belonging._id] = belonging
            return belonging

    # working with borowings
    def borrow_to(self, friend, belonging, when=None):
        """
        borrow one thing to friend
        friend : Friend object
        belonging : Belonging object
        when : datetime or None, then when = now
        """
        url = BASE_URL + URLS['borrowings']
        data = {'what': belonging.id,
                'to_who': friend.id,
                }
        if when is not None:
            data['when'] = dt_when
        reply = self._get_data_post(url, data)
        if reply:
            #friend = self.friend_by_id(reply['to_who'])
            #belonging = self.belonging_by_id(reply['what'])
            borrow = Borrow(
                id=int(reply['id']),
                when=reply['when'],
                what=belonging,
                who=friend,
                returned=reply['returned']
                )
            return borrow
    
    # working with API
    def _get_data_post(self, url, data):
        try:
            if self._token:
                auth_header = {'Authorization': f'Token {self._token}'}
                response = requests.post(url, data=data, headers=auth_header)
            else:
                response = requests.post(url, data=data)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error ocured {http_err}')
        except Exception as err:
            print(f'Unexception error ocured {err}')
        else:
           return response.json()

    def _get_data_get(self, url, param={}):
        if self._token:
            auth_header = {'Authorization': f'Token {self._token}'}
            try:
                if param:
                    response = requests.get(
                        url, headers=auth_header, params=param
                        )
                else:
                    response = requests.get(
                        url, headers=auth_header
                        )
                response.raise_for_status()
            except HTTPError as http_err:
                print(f'HTTP error ocured {http_err}')
            except Exception as err:
                print(f'Unexception error ocured {err}')
            else:
                # print(response.links)
                # print(response.json())
                return response

