import pytest

from modules.accounts.exceptions import AccountBannedException
from modules.utils.service_factories import create_account_control_service, create_names_service, create_proxy_service


async def add_user(mocker, user_id=1, phone='798', first_name='vova1', last_name='vova2', username='vova3'):
    mocker.patch('modules.accounts.account_telethon.AccountTelethon.get_account_information',
                 return_value={
                     'user_id': user_id,
                     'phone': phone,
                     'first_name': first_name,
                     'last_name': last_name,
                     'username': username
                 })
    mocker.patch('modules.accounts.account_telethon.AccountTelethon.hide_active_time',
                 return_value=True)

    await create_account_control_service().import_user(r'A:\pycharm projects\telegram-wrapping\tests\data\test.session')


@pytest.mark.asyncio
async def test_import_without_name(mocker):
    await add_user(mocker)
    account = await create_account_control_service().get_user(1)
    assert account.user_id == 1
    assert account.phone == '798'
    assert account.first_name == 'vova1'
    assert account.last_name == 'vova2'
    assert account.username == 'vova3'
    assert account.categories == ['not_changed']
    assert account.status == 'active'


@pytest.mark.asyncio
async def test_user_fail(mocker):
    await add_user(mocker)
    account = await create_account_control_service().get_user(1)
    assert account is not None
    await create_account_control_service().user_fail(1)
    account = await create_account_control_service().get_user(1)
    assert account.status == 'inactive'


@pytest.mark.asyncio
async def test_get_active(mocker):
    await add_user(mocker)
    await add_user(mocker, 2)
    await add_user(mocker, 3)

    accounts = await create_account_control_service().get_accounts()
    assert list(map(lambda i: i.user_id, accounts)) == [1, 2, 3]
    await create_account_control_service().user_fail(2)
    accounts = await create_account_control_service().get_accounts()
    assert list(map(lambda i: i.user_id, accounts)) == [1, 3]


@pytest.mark.asyncio
async def test_change_user(mocker):
    await add_user(mocker, 1)
    mocker.patch('modules.accounts.account_telethon.AccountTelethon.edit_profile',
                 return_value=True)
    account = await create_account_control_service().get_user(1)
    print(account)
    assert account.categories == ['not_changed']
    await create_account_control_service().change_user_info(
        1, 'fname', 'sname', 'about', 'username', ['male']
    )
    account = await create_account_control_service().get_user(1)
    assert account.user_id == 1
    assert account.first_name == 'fname'
    assert account.last_name == 'sname'
    assert account.about == 'about'
    assert account.username == 'username'
    assert account.categories == ['male']


@pytest.mark.asyncio
async def test_check_user(mocker):
    await add_user(mocker, 1)
    await create_account_control_service().check_user_id(1)
    account = await create_account_control_service().get_user(1)
    assert account.status == 'active'
    mocker.patch('modules.accounts.account_telethon.AccountTelethon.get_account_information',
                 side_effect=AccountBannedException('test'))
    assert account.inactive_reason == ''
    await create_account_control_service().check_user_id(1)
    account = await create_account_control_service().get_user(1)
    assert account.status == 'inactive'
    assert account.inactive_reason == 'test'


@pytest.mark.asyncio
async def test_change_user_name(mocker):
    await create_proxy_service().add_proxies(["asd:pass@8.8.8.8:80", "1.1.1.1:1"], categories=['asd'])
    await create_names_service().add_name(100, 'fname', 'lname', 'mabout', 'muser', None, ['female'])
    name = await create_names_service().get_name(100)
    assert len(await create_names_service().get_names()) == 1
    mocker.patch('modules.proxy.proxy_service.ProxyService.get_random_proxy',
                 return_value=None)
    await add_user(mocker, 10)
    mocker.patch('modules.accounts.account_telethon.AccountTelethon.edit_profile',
                 return_value=True)
    await create_account_control_service().change_user(10)
    account = await create_account_control_service().get_user(10)
    assert account.first_name == 'fname'
    assert account.last_name == 'lname'
    assert account.about == 'mabout'
    assert account.username == name.new_username
    assert account.categories == ['female']


@pytest.mark.asyncio
async def test_import_user_with_name(mocker):
    await create_names_service().add_name(102, 'fname', 'lname', 'mabout', 'muser', None, ['female'])
    name = await create_names_service().get_name(102)
    assert len(await create_names_service().get_names()) == 1
    mocker.patch('modules.accounts.account_telethon.AccountTelethon.edit_profile',
                 return_value=True)
    await add_user(mocker, 109)
    account = await create_account_control_service().get_user(109)
    assert account.first_name == 'fname'
    assert account.last_name == 'lname'
    assert account.about == 'mabout'
    assert account.username == name.new_username
    assert account.categories == ['female']


@pytest.mark.asyncio
async def test_categories(mocker):
    categories = await create_account_control_service().get_categories()
    assert categories == []
    await create_account_control_service().add_category("123")
    await create_account_control_service().add_category("1234")
    await create_account_control_service().add_category("1234")
    categories = await create_account_control_service().get_categories()
    assert set(categories) == {'1234', '123'}
    await create_account_control_service().remove_category("123")
    await create_account_control_service().remove_category("123")
    categories = await create_account_control_service().get_categories()
    assert categories == ['1234']


@pytest.mark.asyncio
async def test_account_categories(mocker):
    await add_user(mocker, user_id=145)
    user = await create_account_control_service().get_user(145)
    user.categories = []
    user.categories = ['1', '1', '', ' ']
    assert user.categories == ['1']
    print(user.categories)
