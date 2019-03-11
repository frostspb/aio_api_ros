# aio_api_ros
async implementation Mikrotik api

**Installation**

```
pip install aio_api_ros
```

**Example of usage**

```python
import asyncio
from aio_api_ros.api_controller import ApiRosController


async def main():
    mk = ApiRosController(
        mk_ip='127.0.0.1', 
        mk_port=8728, 
        mk_user='myuser', 
        mk_psw='mypassword'
    )
    await mk.connect()
    await mk.login()
    mk.talk_word('/ip/hotspot/active/print')
    res = await mk.reader.read(64)
    print(res)
    mk.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
```