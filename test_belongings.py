import pytest
from mintal import Belonging, Friend, User

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
    
def test_add_belonging_object(get_user):
    user_djoser = get_user
    if user_djoser:
        belonging = Belonging(user_djoser, 'umbrella')
        user_djoser.add_belonging(belonging)
        assert belonging.id == BELONGINGS_NUMBER + 1

def test_add_belonging_name(get_user):
    user_djoser = get_user
    things = (
        'screw driver PH2',
        'hammer',
        'swiss knife',
        'tin cup',
        'walkman',
        'reciever',
        )
    if user_djoser:
        for belonging in things:
            #belonging = 'screw driver PH2'
            thing = user_djoser.add_belonging(belonging)
        assert thing.id == BELONGINGS_NUMBER + 1 + len(things)

def test_get_all_belongings(get_user):
    user_djoser = get_user
    user_djoser.get_all_belongings()
    belongings_qty = user_djoser.number_belongings()
    print(f'Number of djoser\'s belongings: {belongings_qty}')
    assert belongings_qty == BELONGINGS_NUMBER + 1 + 6

def test_get_page_belongings(get_user):
    user_djoser = get_user
    belongings, links = user_djoser.get_page_belongings()
    print(belongings)
    print(links)
    assert len(belongings) == PAGE_NUMBER
    assert 'last' in links
    assert 'belongings' in links['last']['url']
