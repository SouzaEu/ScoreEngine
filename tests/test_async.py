import pytest

@pytest.mark.asyncio
async def test_async_exemplo():
    async def soma():
        return 1 + 1
    resultado = await soma()
    assert resultado == 2 