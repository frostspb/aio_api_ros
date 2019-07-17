import asyncio
import hashlib
import binascii
import uuid

from .errors import LoginFailed
from .errors import UnpackValueError
from .unpacker import SentenceUnpacker
from .parser import parse_sentence

ERROR_TAG = '!trap'
DEFAULT_READ_DATA_LEN = 4096


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

    def _get_login_sentence(self):
        """
        Perform login sentence  with challenge argument
        :param challenge_arg:
        :return:
        """
        return [
            "/login",
            "=name=" + self.user,
            "=password=" + self.password
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
        try:
            response_str = data.decode('UTF-8', 'replace')
            res_list = response_str.split('!done')
            str_val = res_list[1]
            res_list = str_val.split('%=ret=')
            res = str(res_list[1])
        except IndexError:
            raise LoginFailed('Getting challenge argument failed')
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

    async def read(self, parse=True, full_answer=False,
                   length=DEFAULT_READ_DATA_LEN):
        """
        Read response from api
        :param parse:
        :param full_answer:
        :param length:
        :return:
        """
        byte_res = b''
        list_res = []
        while True:

            data = await self.reader.read(length)
            if parse:
                try:

                    parsed_data = self._parse_sentence(data, full_answer)
                    list_res += parsed_data
                    byte_res += data

                except UnpackValueError:
                    parse = False
            else:
                byte_res += data

            if '!done' in data.decode():
                res = list_res if parse else byte_res
                break

        return res

    @staticmethod
    def _parse_sentence(data, full_answer=False):
        unpacker = SentenceUnpacker()
        unpacker.feed(data)
        res = [
            parse_sentence(sentence) if full_answer
            else parse_sentence(sentence)[2] for sentence in unpacker
        ]
        return res

    async def login(self):
        """
        Login to api
        :return:
        """
        try:
            self.talk_word(r'/login')
            await self.writer.drain()

            login_sentence = self._get_login_sentence()
            self.talk_sentence(login_sentence)
            await self.writer.drain()
            data = await self.reader.read(64)

            # login failed
            if ERROR_TAG in data.decode():
                raise LoginFailed(self._get_err_message(data))

            return data

        except ConnectionResetError:
            raise LoginFailed('Connection reset by peer')

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
        data = await self.read(parse=False)

        # login failed
        if ERROR_TAG in data.decode():
            result = self._get_result_dict(-1, self._get_err_message(data))

        else:
            result = self._get_result_dict(0, 'OK')
        return result
