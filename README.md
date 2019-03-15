# aio_api_ros

[![Join the chat at https://gitter.im/aio_api_ros/community](https://badges.gitter.im/aio_api_ros/community.svg)](https://gitter.im/aio_api_ros/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![PyPI version](https://badge.fury.io/py/aio-api-ros.svg)](https://badge.fury.io/py/aio-api-ros)
[![Downloads](https://pepy.tech/badge/aio-api-ros)](https://pepy.tech/project/aio-api-ros)
[![star this repo](http://githubbadges.com/star.svg?user=frostspb&repo=aio_api_ros&style=flat)](https://github.com/frostspb/aio_api_ros)
[![fork this repo](http://githubbadges.com/fork.svg?user=frostspb&repo=aio_api_ros&style=flat)](https://github.com/frostspb/aio_api_ros/fork)

async implementation Mikrotik api

**Installation**

```
pip install aio_api_ros
```

**Example of usage**

*Single connection*
```python
import asyncio
from aio_api_ros import create_rosapi_connection

async def main():

    mk = await create_rosapi_connection(
        mk_ip='127.0.0.1',
        mk_port=8728,
        mk_user='myuser',
        mk_psw='mypassword'
    )

    mk.talk_word('/ip/hotspot/active/print')
    res = await mk.read()
    print(res)
    mk.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

```
*Simple connections pool*
```python

import asyncio
from aio_api_ros import create_rosapi_simple_pool

async def main():

    mk = await create_rosapi_simple_pool(
        mk_ip='127.0.0.1',
        mk_port=8728,
        mk_user='myuser',
        mk_psw='mypassword',
        max_size=4
    )

    await mk.talk_word('/ip/hotspot/active/print')
    res = await mk.read()
    print(res)
    mk.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

```
