import asyncio
import hashlib
import binascii

#TODO Add docstring try catch validation
#todo parse response mk for success or fail
# TODO add connections pool
#TODO add tests

class ApiRosController:
    def __init__(self, mk_ip: str, mk_port: int, mk_user: str, mk_psw: str ):
        if not all([mk_ip, mk_port, mk_user, mk_psw]):
            raise RuntimeError('Wrong connection params!')
        self.ip = mk_ip
        self.port = mk_port
        self.user = mk_user
        self.password = mk_psw
        self.writer = None
        self.reader = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.ip, self.port
        )

    def __del__(self):
        self.close()

    @staticmethod
    def to_bytes(str_value: str):
        length = (len(str_value).bit_length() // 8) + 1
        res = len(str_value).to_bytes(length, byteorder='little')
        return res

    def talk_end(self):
        self.writer.write(self.to_bytes(''))
        self.writer.write(''.encode())

    def talk_word(self, str_value: str, send_end=True):
        self.writer.write(self.to_bytes(str_value))
        self.writer.write(str_value.encode())
        if send_end:
            self.talk_end()

    def talk_sentence(self, sentence: list):
        for word in sentence:
            self.talk_word(word, False)
        self.talk_end()

    def close(self):
        self.writer.close()

    def get_login_sentence(self, challenge_arg):
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
    def get_challenge_arg(data):
        response_str = data.decode('UTF-8', 'replace')
        res_list = response_str.split('!done')
        str_val = res_list[1]
        res_list = str_val.split('%=ret=')
        res = str(res_list[1])
        return res

    async def login(self):
        self.talk_word(r'/login')
        await self.writer.drain()
        data = await self.reader.read(64)

        challenge_arg = self.get_challenge_arg(data)
        login_sentence = self.get_login_sentence(challenge_arg)
        self.talk_sentence(login_sentence)
        await self.writer.drain()
        data = await self.reader.read(64)

        return data

    async def login_client(self, client_ip: str, client_login: str,
                           client_psw: str):
        sentence = [
            '/ip/hotspot/active/login',
            '=ip={}'.format(client_ip),
            '=user={}'.format(client_login),
            '=password={}'.format(client_psw),
        ]
        self.talk_sentence(sentence)
        result = await self.reader.read(64)
        return result