import pytest

from modules.names.parsing_service import tasks
from modules.utils.service_factories import create_parsing_service, create_account_control_service, create_names_service

cid = 0


async def parse_chat(self, link: str, offset: int, block: int, image_out: str, delay: int, categories: list[str],
                     names_service):
    global cid
    for i in range(block):
        await names_service.add_name(cid, "firstName", "lastname", "about", "username", None, categories)
        cid += 1


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
async def test_simple(mocker):
    mocker.patch('modules.names.parsing_telethon.ParsingTelethon.parse_chat',
                 new=parse_chat)
    mocker.patch('asyncio.sleep', return_value=True)
    await add_user(mocker)

    names = await create_names_service().get_names()
    for i in names:
        await create_names_service().delete_name(i.id)

    await create_parsing_service().start_parsing("123", 60, 30, 1, 1, 1, ['male'])
    parsing = await create_parsing_service().get_parsings()
    _parsing = await create_parsing_service().get_parsing(1)
    assert parsing != []
    assert parsing == [_parsing]
    assert len(tasks) != 0
    await tasks[1]
    parsing = await create_parsing_service().get_parsings()
    assert parsing == []
    assert len(await create_names_service().get_names()) == 60
    for n in await create_names_service().get_names():
        assert n.categories == ['male']
    await create_parsing_service().stop_parsing(1)
    parsing = await create_parsing_service().get_parsings()
    assert parsing == []


@pytest.mark.asyncio
async def test_remove(mocker):
    mocker.patch('modules.names.parsing_telethon.ParsingTelethon.parse_chat',
                 new=parse_chat)
    mocker.patch('asyncio.sleep', return_value=True)
    await add_user(mocker)

    names = await create_names_service().get_names()
    for i in names:
        await create_names_service().delete_name(i.id)

    await create_parsing_service().start_parsing("123", 60, 30, 1, 1, 1, ['male'])
    parsing = await create_parsing_service().get_parsings()
    assert parsing != []
    assert len(tasks) != 0
    await create_parsing_service().stop_parsing(parsing[0].id)
    parsing = await create_parsing_service().get_parsings()
    assert parsing == []
    assert len(tasks) == 0
