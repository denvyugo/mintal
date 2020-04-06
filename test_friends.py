import pytest
from mintal import Belonging, Friend, User

FRIENDS_NUMBER = 12
BELONGINGS_NUMBER = 0
PAGE_NUMBER = 5

@pytest.fixture
def get_user():
    """
    get user object by name, password for working
    """
    user = User('djoser')
    if user.login('alpine12'):
        return user

def test_add_friend_object(get_user):
    user_djoser = get_user
    if user_djoser:
        friend = Friend(user_djoser, 'James Barnes')
        user_djoser.add_friend(friend)
        assert friend.id == FRIENDS_NUMBER + 1

def test_add_friend_name(get_user):
    user_djoser = get_user
    if user_djoser:
        user_djoser.add_friend('Sam Wilson')
    assert user_djoser.number_friends() == 1    

def test_friend_id(get_user):
    user_djoser = get_user
    friend = Friend(user_djoser, 'Tony Stark')
    with pytest.raises(TypeError):
        friend.id = 'Iron'

def test_get_friends(get_user):
    user_djoser = get_user
    user_djoser.get_friends()
    friends_qty = user_djoser.number_friends()
    print(f'Number of djoser\'s friends: {friends_qty}')
    assert friends_qty == PAGE_NUMBER

def test_get_all_friends(get_user):
    user_djoser = get_user
    user_djoser.get_all_friends()
    friends_qty = user_djoser.number_friends()
    print(f'Number of djoser\'s friends: {friends_qty}')
    assert friends_qty == FRIENDS_NUMBER + 2

def test_get_page_friends(get_user):
    user_djoser = get_user
    friends, links = user_djoser.get_page_friends()
    print(friends)
    print(links)
    assert len(friends) == PAGE_NUMBER
    assert 'next' in links
    assert 'friends' in links['next']['url']
    
