import asyncio

from aio_api_ros.connection import ApiRosConnection


class ApiRosSimplePool:
    def __init__(self, mk_ip: str, mk_port: int, mk_user: str, mk_psw: str,
                 max_size: int, loop=None):
        self.ip = mk_ip
        self.port = mk_port
        self.user = mk_user
        self.password = mk_psw
        self._max_size = max_size
        if loop is None:
            self._loop = asyncio.get_event_loop()
        else:
            self._loop = loop
        conns = [self.create_connection_object() for _ in range(max_size)]
        self._pool = conns

    def __await__(self):
        for connection in self._pool:
            yield from connection.connect().__await__()
            yield from connection.login().__await__()
        return self

    def create_connection_object(self):
        return ApiRosConnection(
            mk_user=self.user,
            mk_psw=self.password,
            mk_ip=self.ip,
            mk_port=self.port,
            loop=self._loop
        )

    @property
    def max_size(self):
        """Maximum pool size."""
        return self._max_size

    def get_conn(self, fut=None):
        if fut is None:
            fut = self._loop.create_future()

        for connection in self._pool:
            if not connection.used:
                connection.used = True
                fut.set_result(connection)
                break
            else:
                self._loop.call_soon(self.get_conn, fut)
        return fut

    def release(self, conn):
        if not conn.used:
            return
        for connection in self._pool:
            if connection.uuid != conn.uuid:
                continue
            connection.used = False
            break

    def close(self):
        for connection in self._pool:
            connection.close()

    async def talk_word(self, str_value: str, send_end=True):
        con = await self.get_conn()
        con.talk_word(str_value, send_end)
        self.release(con)

    async def talk_sentence(self, sentence: list):
        con = await self.get_conn()
        con.talk_sentence(sentence)
        self.release(con)

    async def read(self, length=128):
        con = await self.get_conn()
        res = await con.read(length)
        self.release(con)
        return res

    async def login_client(self, client_ip: str, client_login: str,
                           client_psw: str):

        await self.login_client(client_ip, client_login, client_psw)
        result = await self.read()
        return result
