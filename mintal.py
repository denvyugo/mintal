"""
working with DRF application 'rental'
rev.01
"""

import abc
import requests
from datetime import datetime as dt
from datetools import convert_datetime, local_datetime_string
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
        return f'Belonging: {self._name}'

    def __repr__(self):
        return f'<Belonging object: Belonging.name = {self._name}>'


class Borrow(Thing):
    """
    user's borrow class
    """
    def __init__(self, user):
        self._user = user
        self._id = 0
        self._when = None
        self._what = None
        self._who = None
        self._returned = None

    def load_data(self, data):
        self._user._load_borrow_data(self, data)

    @property
    def returned(self):
        return self._returned

    @returned.setter
    def returned(self, returned_date):
        if returned_date:
            dt_return = convert_datetime(returned_date)
            self._returned = dt_return

    @property
    def when(self):
        return self._when

    @when.setter
    def when(self, when_date):
        if when_date:
            dt_when = convert_datetime(when_date)
            self._when = dt_when

    @property
    def who(self):
        return self._who

    @who.setter
    def who(self, to_friend):
        if isinstance(to_friend, Friend):
            self._who = to_friend
        else:
            raise TypeError('to_friend should be Friend object')

    @property
    def what(self):
        return self._what

    @what.setter
    def what(self, thing):
        if isinstance(thing, Belonging):
            self._what = thing
        else:
            raise TypeError('thing argument should be Belonging object')


class User:
    """
    user class for working with 'rental'
    """
        
    def __init__(self):
        self._username = ''
        self._friends = {}
        self._belongings = {}
        self._borrowings = {}
        self._token = None

    def login(self, username, password):
        """
        get token
        """
        url = BASE_URL + 'auth/token/login/'
        self._username = username
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
        url = BASE_URL + 'auth/token/logout/'
        self._get_data_post(url)
        self._token = None
        return self._token

    def register(self, username, password):
        """
        register new user
        """
        url = BASE_URL + 'auth/users/'
        self._username = username
        data = {
            'username': self._username,
            'password': password
            }
        reply = self._get_data_post(url, data)
        if reply:
            self._id = int(reply['id'])
            return self._id

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token_value):
        self._token = token_value

    def _create_thing(self, thing):
        """
        create an instance of concreate thing object
        """
        if thing.lower() == 'friend':
            thing_object = Friend(self)
        elif thing.lower() == 'belonging':
            thing_object = Belonging(self)
        elif thing.lower() == 'borrowing':
            thing_object = Borrow(self)
        else:
            # TODO: ValueError
            thing_object = None
        return thing_object

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
                    thing_object = self._create_thing(thing)
                    thing_object.load_data(data)
                    package[thing_object.id] = thing_object
            url = ''
            links = response.links
            if links:
                if 'next' in links:
                    url = links['next']['url']
        return reply

    def _get_thing(self, url, package, thing):
        """
        get a one thing by url
        """
        response = self._get_data_get(url)
        if response:
            reply = response.json()
            thing_object = self._create_thing(thing)
            thing_object.load_data(reply)
            package[thing_object.id] = thing_object
            return thing_object

    def _get_page_things(self, url, package, thing):
        """
        get a list of Thing (friend, belonging) and a links
        """
        response = self._get_data_get(url)
        reply = response.json()
        if reply:
            things = []
            for data in reply:
                thing_object = self._create_thing(thing)
                thing_object.load_data(data)
                if not thing_object.id in package:
                    package[thing_object.id] = thing_object
                things.append(thing_object)
            return things, response.links

    # working with friends
    def _load_friend_data(self, friend, data):
        """
        load data into concrete friend object
        """
        friend.id = data['id']
        friend.overdue = bool(data['has_overdue'])
        friend._name = data['name']

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
        if not friend_id in self._friends:
            url = f"{BASE_URL}{URLS['friends']}{friend_id}/"
            self._get_thing(url, self._friends, 'friend')
        return self._friends[friend_id]
        
    # working with belongings
    def _load_belonging_data(self, belonging, data):
        """
        load data into concrete belonging object
        """
        belonging.id = data['id']
        belonging._name = data['name']
        if 'is_borrowed' in data:
            belonging.borrowed = data['is_borrowed']

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
                self._belongings[belonging.id] = belonging

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
        if not belonging_id in self._belongings:
            url = f"{BASE_URL}{URLS['belongings']}{belonging_id}/"
            self._get_thing(url, self._belongings, 'belonging')
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
            self._belongings[belonging.id] = belonging
            return belonging

    # working with borrowings
    def _load_borrow_data(self, borrow, data):
        """
        load data to borrow object
        """
        friend = self.friend_by_id(int(data['to_who']))
        belonging = self.belonging_by_id(int(data['what']))
        borrow.id = int(data['id'])
        borrow.when = data['when']
        borrow.what = belonging
        borrow.who = friend
        borrow.returned = data['returned']

    def get_borrowings(self):
        """
        get a borrowings list
        """
        url = BASE_URL + URLS['borrowings']
        response = self._get_data_get(url)
        reply = response.json()
        if reply:
            for data in reply:
                borrow = Borrow(self)
                borrow.load_data(data)
                self._borrowings[borrow.id] = borrow

    def borrow_by_id(self, borrow_id):
        """
        get borrow by id from self package borrows
        """
        if not borrow_id in self._borrowings:
            url = f"{BASE_URL}{URLS['borrowings']}{borrow_id}/"
            self._get_thing(url, self._borrowings, 'borrowing')
        return self._borrowings[borrow_id]

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
            data['when'] = local_datetime_string(when)
        else:
            data['when'] = local_datetime_string(dt.now())
        reply = self._get_data_post(url, data)
        if reply:
            borrow = Borrow(self)
            borrow.load_data(reply)
            self._borrowings[borrow.id] = borrow
            return borrow

    def get_missing(self):
        """
        get borrowings which was borrowed
        return list of borrowings
        """
        url = BASE_URL + URLS['borrowings']
        params = {'missing': True}
        response = self._get_data_get(url, params)
        reply = response.json()
        if reply:
            borrowings = []
            for data in reply:
                borrow = Borrow(self)
                borrow.load_data(data)
                borrowings.append(borrow)
            return borrowings

    def get_overdue(self):
        """
        get borrowings which was borrowed too long
        return list of borrowings
        """
        url = BASE_URL + URLS['borrowings']
        params = {'overdue': True}
        response = self._get_data_get(url, params)
        reply = response.json()
        if reply:
            borrowings = []
            for data in reply:
                borrow = Borrow(self)
                borrow.load_data(data)
                borrowings.append(borrow)
            return borrowings

    def friend_borrowings(self, friend):
        """
        get all friend's borrowings
        """
        url = f"{BASE_URL}{URLS['friends']}{friend.id}/borrowings/"
        response = self._get_data_get(url)
        reply = response.json()
        if reply:
            borrowings = []
            for data in reply:
                borrow = Borrow(self)
                borrow.load_data(data)
                borrowings.append(borrow)
            return borrowings

    def borrow_return(self, borrow, when=None):
        """
        make a notice when a belonging was returned
        borrow : Borrow object
        when : datetime object, if None than returned now
        """
        if when is None:
            returned = local_datetime_string(dt.now())
        else:
            returned = local_datetime_string(when)
        url = f"{BASE_URL}{URLS['borrowings']}{borrow.id}/"
        data = {'returned': returned}
        reply = self._get_data_patch(url, data)
        if reply:
            borrow.returned = when
    
    # working with API
    def _get_data_post(self, url, data=None):
        try:
            if self._token:
                auth_header = {'Authorization': f'Token {self._token}'}
                if data:
                    response = requests.post(url, data=data, headers=auth_header)
                else:
                    response = requests.post(url, headers=auth_header)
            else:
                response = requests.post(url, data=data)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred {http_err}')
        except Exception as err:
            print(f'Unexpected error occurred {err}')
        else:
            if response.status_code != 204:
                return response.json()
        
    def _get_data_patch(self, url, data):
        try:
            if self._token:
                auth_header = {'Authorization': f'Token {self._token}'}
                response = requests.patch(url, data=data, headers=auth_header)
            else:
                response = requests.patch(url, data=data)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred {http_err}')
        except Exception as err:
            print(f'Unexpected error occurred {err}')
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
                print(f'HTTP error occurred {http_err}')
            except Exception as err:
                print(f'Unexpected error occurred {err}')
            else:
                return response

