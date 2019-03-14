import asyncio
import hashlib
import binascii
import uuid

from .errors import LoginFailed

ERROR_TAG = '!trap'


class ApiRosConnection:
    """
    Connection to Mikrotik api
    """
    def __init__(self, mk_ip: str, mk_port: int, mk_user: str, mk_psw: str,
                 loop=None):
        if not all([mk_ip, mk_port, mk_user, mk_psw]):
            raise RuntimeError('Wrong connection params!')
        self.ip = mk_ip
        self.port = mk_port
        self.user = mk_user
        self.password = mk_psw
        self.writer = None
        self.reader = None
        self._loop = loop
        self._uuid = uuid.uuid1()
        self.used = False

    def __del__(self):
        self.close()

    def __repr__(self):
        return 'Connection to %s:%s id=%s' % (self.ip, self.port, self.uuid)

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.ip, self.port, loop=self._loop
        )

    @property
    def uuid(self):
        """
        uuid of connection
        :return: str
        """
        return self._uuid

    @staticmethod
    def _to_bytes(str_value: str):
        """
        Convert string to bytes
        :param str_value: str
        :return: bytes
        """
        length = (len(str_value).bit_length() // 8) + 1
        res = len(str_value).to_bytes(length, byteorder='little')
        return res

    def _talk_end(self):
        """
        Send EOC (end of command) to mikrotik api
        :return:
        """
        self.writer.write(self._to_bytes(''))
        self.writer.write(''.encode())

    def talk_word(self, str_value: str, send_end=True):
        """
        Send word to mikrotik
        :param str_value: command
        :param send_end: bool Flag - send end after this command
        :return:
        """
        self.writer.write(self._to_bytes(str_value))
        self.writer.write(str_value.encode())
        if send_end:
            self._talk_end()

    def talk_sentence(self, sentence: list):
        """
        Send list of commands
        :param sentence: Send list of commands
        :return:
        """
        for word in sentence:
            self.talk_word(word, False)
        self._talk_end()

    def close(self):
        """
        Close connection
        :return:
        """
        self.writer.close()

    def _get_login_sentence(self, challenge_arg):
        """
        Perform login sentence  with challenge argument
        :param challenge_arg:
        :return:
        """
        md = hashlib.md5()
        md.update(b'\x00')
        md.update(self.password.encode('UTF-8'))

        challenge = binascii.unhexlify(challenge_arg.replace('\x00', ''))

        md.update(challenge)
        return [
            "/login",
            "=name=" + self.user,
            "=response=00" + binascii.hexlify(md.digest()).decode('UTF-8')
        ]

    @staticmethod
    def _get_err_message(data):
        """
        Parse error message from mikrotik response
        :param data:
        :return:
        """
        return data.decode().split('=message=')[1].split('\x00')[0]

    @staticmethod
    def _get_challenge_arg(data):
        """
        Parse from mikrotik response challenge argument
        :param data:
        :return:
        """
        response_str = data.decode('UTF-8', 'replace')
        res_list = response_str.split('!done')
        str_val = res_list[1]
        res_list = str_val.split('%=ret=')
        res = str(res_list[1])
        return res

    @staticmethod
    def _get_result_dict(code: int, message: str) -> dict:
        """
        Return dict like {'code': 0, 'message': 'OK}
        :param code:
        :param message:
        :return:
        """
        return {'code': code, 'message': message}

    async def read(self, length=128):
        """
        Read response from api
        :param length:
        :return:
        """
        return await self.reader.read(length)

    async def login(self):
        """
        Login to api
        :return:
        """
        self.talk_word(r'/login')
        await self.writer.drain()
        data = await self.reader.read(64)
        challenge_arg = self._get_challenge_arg(data)
        login_sentence = self._get_login_sentence(challenge_arg)
        self.talk_sentence(login_sentence)
        await self.writer.drain()
        data = await self.reader.read(64)
        # login failed
        if ERROR_TAG in data.decode():
            raise LoginFailed(self._get_err_message(data))

        return data

    async def login_client(self, client_ip: str, client_login: str,
                           client_psw: str):
        """
        Login client to mikrotik
        :param client_ip:
        :param client_login:
        :param client_psw:
        :return:
        """
        sentence = [
            '/ip/hotspot/active/login',
            '=ip={}'.format(client_ip),
            '=user={}'.format(client_login),
            '=password={}'.format(client_psw),
        ]
        self.talk_sentence(sentence)
        data = await self.read()

        # login failed
        if ERROR_TAG in data.decode():
            result = self._get_result_dict(-1, self._get_err_message(data))

        else:
            result = self._get_result_dict(0, 'OK')
        return result
