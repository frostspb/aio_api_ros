import asyncio
from aio_api_ros.creators import create_rosapi_connection

async def main():

    mk = await create_rosapi_connection(
        mk_ip='172.17.54.51',
        mk_port=8728,
        mk_user='api_bot8fl',
        mk_psw='gTjc%*ked%knqp'
    )

    mk.talk_word('/ip/hotspot/active/print')
    res = await mk.read()
    print(res)
    mk.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()