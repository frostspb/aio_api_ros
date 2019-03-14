from .connection import ApiRosConnection
from .simple_pool import ApiRosSimplePool


async def create_rosapi_connection(mk_ip: str, mk_port: int, mk_user: str,
                                   mk_psw: str, loop=None):
    connection = ApiRosConnection(mk_ip=mk_ip, mk_port=mk_port,
                                  mk_user=mk_user, mk_psw=mk_psw, loop=loop)

    await connection.connect()
    await connection.login()
    return connection


async def create_rosapi_simple_pool(mk_ip: str, mk_port: int, mk_user: str,
                                    mk_psw: str, max_size: int, loop=None):
    simple_pool = await ApiRosSimplePool(mk_ip=mk_ip, mk_port=mk_port,
                                         mk_user=mk_user, mk_psw=mk_psw,
                                         max_size=max_size, loop=loop)
    return simple_pool
