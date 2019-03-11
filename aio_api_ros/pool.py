import asyncio
import collections
import types

class ApiRosPool:
    def __init__(self, mk_ip: str, mk_port: int, mk_user: str, mk_psw: str,
                 min_size: int, max_size: int):
        self.ip = mk_ip
        self.port = mk_port
        self.user = mk_user
        self.password = mk_psw
        self.min_size = min_size
        self.max_size = max_size
        self._pool = collections.deque(maxlen=max_size)
        self._used = set()
        self._acquiring = 0
        #self._cond = asyncio.Condition(lock=Lock(loop=loop), loop=loop)
        self._close_state = asyncio.Event(loop=loop)
        self._close_waiter = None
