import pytest

from modules.utils.service_factories import create_names_service


@pytest.mark.asyncio
async def test_simple():
    await create_names_service().add_name(100, 'fname', 'lname', 'mabout', 'muser', None, ['female'])
    name = await create_names_service().get_name(100)
    rname = await create_names_service().pop_random_name()
    for n in [name, rname]:
        assert n.first_name == 'fname'
        assert n.last_name == 'lname'
        assert n.about == 'mabout'
        assert n.username == 'muser'
        assert n.new_username != n.username
        assert n.categories == ['female']

    await create_names_service().add_name(1001, '1fname', '1lname', '1mabout', '1muser', None, [])
    name2 = await create_names_service().get_name(1001)
    assert await create_names_service().get_names() == [name, name2]
    await create_names_service().delete_name(1001)
    assert await create_names_service().get_names() == [name]
    assert await create_names_service().get_name(1001) is None
