from requests import get
import asyncio
import aiohttp

url = 'http://puparass.pythonanywhere.com/api/users/'
SECRET_PASSWORD = 'yEChQDWrLCXg3zQPvJeEuY25e3EOn0'


async def get_user(telegram_id, session):
    async with session.get('http://puparass.pythonanywhere.com/api/users/' + str(telegram_id), headers={'password': SECRET_PASSWORD}) as response:
        a = await response.json()
        print(a)


async def main():
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in range(10):
            task = asyncio.create_task(get_user(i, session))
            tasks.append(task)
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
    print('asf')
