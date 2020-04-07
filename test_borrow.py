import pytest

import random
from datetime import datetime as dt
from mintal import Belonging, Borrow, Friend, User

FRIENDS_NUMBER = 12
BELONGINGS_NUMBER = 7
PAGE_NUMBER = 5

@pytest.fixture
def get_user():
    """
    get user object by name, password for working
    """
    user = User('djoser')
    if user.login('alpine12'):
        return user

def test_borrow(get_user):
    user_djoser = get_user
    if user_djoser:
        user_djoser.get_all_friends()
        friend = user_djoser.friend_by_id(random.randint(1, FRIENDS_NUMBER))
        user_djoser.get_all_belongings()
        belonging_id = random.randint(1, BELONGINGS_NUMBER)
        belonging = user_djoser.belonging_by_id(belonging_id)
        when = dt.strptime('2020-01-12 20:15:00', '%Y-%m-%d %H:%M:%S')
        borrow = user_djoser.borrow_to(friend, belonging, when)
        # borrow = user_djoser.borrow_to(friend, belonging)
        assert borrow.id == 1

def test_borrowed_thing(get_user):
    user_djoser = get_user
    if user_djoser:
        #user_djoser.get_all_friends()
        #for i in range(1, FRIENDS_NUMBER + 1):
        #    friend = user_djoser.friend_by_id(i)
        user_djoser.get_all_belongings()
        is_borrowed = False
        for i in range(1, BELONGINGS_NUMBER + 1):
            belonging = user_djoser.belonging_by_id(i)
            if belonging.borrowed == True:
                is_borrowed = belonging.borrowed
                break
        assert is_borrowed == True

def test_none_borrow_by_id(get_user):
    user_djoser = get_user
    if user_djoser:
        with pytest.raises(KeyError):
            borrow = user_djoser.borrow_by_id(2)

def test_borrow_return(get_user):
    user_djoser = get_user
    if user_djoser:
        user_djoser.get_all_friends()
        user_djoser.get_all_belongings()
        user_djoser.get_borrowings()
        borrow = user_djoser.borrow_by_id(1)
        user_djoser.borrow_return(borrow)
        user_djoser.get_borrowings()
        borrow = user_djoser.borrow_by_id(1)
        assert dt.strftime(borrow.returned, '%Y-%m-%d %H:%M') \
               == dt.strftime(dt.now(), '%Y-%m-%d %H:%M')
