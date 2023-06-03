import pytest

from modules.subscriptions.subscriptions_service import tasks
from modules.utils.service_factories import create_account_control_service, create_subscriptions_service

cid = 0


async def add_user(mocker, user_id=1, phone='798', first_name='vova1', last_name='vova2', username='vova3'):
    mocker.patch('modules.accounts.account_telethon.AccountTelethon.get_account_information',
                 return_value={
                     'user_id': user_id,
                     'phone': phone,
                     'first_name': first_name,
                     'last_name': last_name,
                     'username': username
                 })
    await create_account_control_service().import_user(r'A:\pycharm projects\telegram-wrapping\tests\data\test.session')


async def add_user(mocker, user_id=1, phone='798', first_name='vova1', last_name='vova2', username='vova3'):
    mocker.patch('modules.accounts.account_telethon.AccountTelethon.get_account_information',
                 return_value={
                     'user_id': user_id,
                     'phone': phone,
                     'first_name': first_name,
                     'last_name': last_name,
                     'username': username
                 })
    await create_account_control_service().import_user(r'A:\pycharm projects\telegram-wrapping\tests\data\test.session')



async def sleep(time):
    return True


async def create_task(coro):
    return True


@pytest.mark.asyncio
async def test_create(mocker):
    mocker.patch('modules.accounts.account_telethon.AccountTelethon.subscribe_channel_by_link',
                 return_value=True)
    mocker.patch('asyncio.sleep', new=sleep)

    users = await create_account_control_service().get_accounts()
    for user in users:
        await create_account_control_service().user_fail(user.user_id)
    await add_user(mocker)

    await create_subscriptions_service().create_subscription('123', [[20000, 30000, 1]], [])
    sub = await create_subscriptions_service().get_subscriptions()
    assert len(sub) == 1
    assert sub[0].status == 'pause'
    assert 20000 <= sub[0].timeline[0].time_delay <= 30000
    assert sub[0].timeline[0].account_id is None
    assert sub[0].timeline[0].result == 'wait'
    await create_subscriptions_service().change_subscription_status(sub[0].id, 'active')
    await tasks[0]
    sub = await create_subscriptions_service().get_subscriptions()
    assert len(sub) == 1
    assert sub[0].status == 'finished'
    assert 20000 <= sub[0].timeline[0].time_delay <= 30000
    assert sub[0].timeline[0].account_id == 1
    assert sub[0].timeline[0].result == 'process'

    await create_subscriptions_service().change_subscription_status(sub[0].id, 'pause')
    sub = await create_subscriptions_service().get_subscriptions()
    assert sub[0].status == 'pause'
