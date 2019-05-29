"""
This is an adapted code from this repository
https://github.com/mrin/miktapi
"""
import struct

from .errors import BufferFull
from .errors import OutOfData
from .errors import UnknownControlByteError
from .errors import UnpackValueError


class SentenceUnpacker(object):
    def __init__(self, encoding='ASCII', max_buffer_size=0):
        self._buffer = bytearray()
        self._buf_o = 0
        self._max_buffer_size = max_buffer_size or 2**31-1
        self._sentence = None
        self._sentence_o = 0
        self._zero_b = b'\x00'
        self._encoding = encoding

    def feed(self, next_bytes):
        if isinstance(next_bytes, bytes):
            next_bytes = bytearray(next_bytes)
        if (len(self._buffer) + len(next_bytes)) > self._max_buffer_size:
            raise BufferFull
        self._buffer.extend(next_bytes)

    @staticmethod
    def _decode_word_len_num_bytes(first_byte):
        try:
            length = ord(first_byte)
            if length < 128:
                return 1
            elif length < 192:
                return 2
            elif length < 224:
                return 3
            elif length < 240:
                return 4
            else:
                raise UnknownControlByteError()
        except (TypeError, UnknownControlByteError):
            raise UnpackValueError(
                'Unknown control byte {}'.format(first_byte)
            )

    @staticmethod
    def _decode_word_len(length_b):
        nb = len(length_b)
        if nb < 2:
            offset = b'\x00\x00\x00'
            xor = 0
        elif nb < 3:
            offset = b'\x00\x00'
            xor = 0x8000
        elif nb < 4:
            offset = b'\x00'
            xor = 0xC00000
        elif nb < 5:
            offset = b''

            xor = 0xE0000000

        else:
            raise UnpackValueError(
                'Unable to decode length {}'.format(length_b)
            )
        decoded = struct.unpack('!I', (offset + length_b))[0]
        decoded ^= xor
        return decoded

    def _read_cur_sentence(self, size):
        r = self._sentence[self._sentence_o:self._sentence_o + size]
        if not r:
            raise UnpackValueError('Unexpected byte sequence')
        self._sentence_o += size
        return r

    def _read_cur_sentence_word(self):
        fb = self._read_cur_sentence(1)
        if fb == self._zero_b:
            return fb
        w_len_b_cnt = self._decode_word_len_num_bytes(fb)
        if w_len_b_cnt > 1:
            w_len_b = fb + self._read_cur_sentence(w_len_b_cnt - 1)
        else:
            w_len_b = fb
        w_len = self._decode_word_len(w_len_b)
        return self._read_cur_sentence(w_len).decode(
            encoding=self._encoding,
            errors='strict'
        )

    def _unpack(self):
        zero_b_pos = self._buffer.find(self._zero_b, self._buf_o)
        if zero_b_pos != -1:
            self._sentence = self._buffer[0:zero_b_pos + 1]
            self._sentence_o = 0
            del self._buffer[0:zero_b_pos + 1]
            self._buf_o = 0
            return tuple(
                word for word in iter(
                    self._read_cur_sentence_word, self._zero_b
                )
            )
        else:
            self._buf_o = len(self._buffer)
            raise OutOfData

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self._unpack()
        except OutOfData:
            raise StopIteration
