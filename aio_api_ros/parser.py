"""
This is an adapted code from this repository
https://github.com/mrin/miktapi
"""

from .errors import ParseException


CAST_MAP = {'yes': True, 'true': True, 'no': False, 'false': False}


def parse_word(word, cast_int=True, cast_bool=True):
    if word.startswith('!'):
        res = ('reply_word', word)
    else:
        parts = word.split('=')
        if len(parts) == 1:
            res = ('message', parts[0])
        else:
            if parts[0] == '':
                del parts[0]
            len_parts = len(parts)

            if len_parts == 1:
                res = (parts[0], '')
            elif len_parts == 2:
                res = (parts[0], cast_by_map(parts[1], cast_int, cast_bool))
            elif len_parts > 2:
                res = [
                    parts[0],
                    [
                        cast_by_map(v, cast_int, cast_bool) for v
                        in parts[1:len_parts]
                    ],
                ]
            else:
                raise ParseException('Unexpected word format {}'.format(word))
    return res


def parse_sentence(sentence, cast_int=True, cast_bool=True):
    reply_word = sentence[0]
    if not reply_word.startswith('!'):
        raise ParseException('Unexpected reply word')
    if len(sentence) > 1 and sentence[1].startswith('.tag'):
        tag_word = parse_word(sentence[1], cast_int=False, cast_bool=False)[1]
        words = sentence[2:]
    else:
        tag_word = None
        words = sentence[1:]
    return (
        reply_word,
        tag_word,
        dict(parse_word(w, cast_int, cast_bool) for w in words),
    )


def cast_by_map(v, cast_int, cast_bool):
    if cast_int:
        try:
            return int(v)
        except ValueError:
            pass
    if cast_bool:
        return CAST_MAP.get(v, v)
    return v
