import re

import requests

from dataclasses import dataclass
from IPython.display import HTML

GENESIS = 'Genesis'
EXODUS = 'Exodus'
LEVITICUS = 'Leviticus'
NUMBERS = 'Numbers'
DEUTERONOMY = 'Deuteronomy'
JOSHUA = 'Joshua'
JUDGES = 'Judges'
RUTH = 'Ruth'
FIRST_SAMUEL = '1+Samuel'
SECOND_SAMUEL = '2+Samuel'
FIRST_KINGS = '1+Kings'
SECOND_KINGS = '2+Kings'
FIRST_CHRONICLES = '1+Chronicles'
SECOND_CHRONICLES = '2+Chronicles'
EZRA = 'Ezra'
NEHEMIAH = 'Nehemiah'
ESTHER = 'Esther'
JOB = 'Job'
PSALMS = 'Psalms'
PROVERBS = 'Proverbs'
ECCLESIASTES = 'Ecclesiastes'
SONG_OF_Songs = 'Song+of+Songs'
ISAIAH = 'Isaiah'
JEREMIAH = 'Jeremiah'
LAMENTATIONS = 'Lamentations'
EZEKIEL = 'Ezekiel'
DANIEL = 'Daniel'
HOSEA = 'Hosea'
JOEL = 'Joel'
AMOS = 'Amos'
OBADIAH = 'Obadiah'
JONAH = 'Jonah'
MICAH = 'Micah'
NAHUM = 'Nahum'
HABAKKUK = 'Habakkuk'
ZEPHANIAH = 'Zephaniah'
HAGGAI = 'Haggai'
ZECHARIAH = 'Zechariah'
MALACHI = 'Malachi'
MATTHEW = 'Matthew'
MARK = 'Mark'
LUKE = 'Luke'
JOHN = 'John'
ACTS = 'Acts'
ROMANS = 'Romans'
FIRST_CORINTHIANS = '1+Corinthians'
SECOND_CORINTHIANS = '2+Corinthians'
GALATIANS = 'Galatians'
EPHESIANS = 'Ephesians'
PHILIPPIANS = 'Philippians'
COLOSSIANS = 'Colossians'
FIRST_THESSALONIANS = '1+Thessalonians'
SECOND_THESSALONIANS = '2+Thessalonians'
FIRST_TIMOTHY = '1+Timothy'
SECOND_TIMOTHY = '2+Timothy'
TITUS = 'Titus'
PHILEMON = 'Philemon'
HEBREWS = 'Hebrews'
JAMES = 'James'
FIRST_PETER = '1+Peter'
SECOND_PETER = '2+Peter'
FIRST_JOHN = '1+John'
SECOND_JOHN = '2+John'
THIRD_JOHN = '3+John'
JUDE = 'Jude'
REVELATION = 'Revelation'

BASE_API = 'https://bible-api.com/'


def build_verse_api_range_identifier(chapter, start, end):
    out = f'{chapter}'
    if start != -1:
        out += f':{start}'
    if end != -1:
        out += f'-{end}'
    return out


def normalize_verse(verse):
    return verse + ((-1,) * (3 - len(verse)))


def build_api_url(book, *verses):
    formatted_verse_refs = ','.join(build_verse_api_range_identifier(chapter, start, end) for chapter, start, end in map(normalize_verse, verses))
    return f'{BASE_API}{book}+{formatted_verse_refs}'  # ?translation=kjv'


class VerseInfo:
    def __init__(self, verse_dict: dict):
        self.chapter = verse_dict['chapter']
        self.verse = verse_dict['verse']
        self.text = verse_dict['text']
        self.book_name = verse_dict['book_name']

    @classmethod
    def from_response(cls, response: requests.Response):
        return [VerseInfo(verse_dict) for verse_dict in response.json()['verses']]


@dataclass
class GetVerseResult:
    text: str
    response: requests.Response
    verses: list['VerseInfo']
    url: str
    reference: str


def _str_verse_ref_to_tuple(value: str) -> tuple[int, int, int]:
    if m := re.match(r'(\d+):(\d+)-(\d+)', value):
        return int(m[1]), int(m[2]), int(m[3])
    if m := re.match(r'(\d+):(\d+)', value):
        return int(m[1]), int(m[2]), -1
    if m := re.match(r'(\d+)', value):
        return int(m[1]), -1, -1
    return -1, -1, -1


def _verse_ref_to_tuple(value):
    match value:
        case tuple():
            return value
        case list():
            return tuple(value)
        case slice() as s:
            return (s.start or -1, s.stop or -1, s.step or -1)
        case int():
            return (value, -1, -1)
        case str():
            return _str_verse_ref_to_tuple(value)
        case _:
            raise ValueError(f'expected type ({tuple}, {list}, or {slice}), actually got: {type(value)}')


def get_verse(book, *verses):
    verses = [_verse_ref_to_tuple(v) for v in verses]
    r = requests.get(url := build_api_url(book, *verses))
    r_json = r.json()
    return GetVerseResult(text=r_json['text'], response=r, verses=VerseInfo.from_response(r), url=url,
                          reference=r_json['reference'])


def generate_css_style():
    return ('<style>'
            + '''
.verse_ref {
    font-size: 3em;
    font-family: Baskerville, serif;

}

.verse_text {
    font-size: 2em;
    font-family: Baskerville, serif;
    font-weight: normal;
}'''
            + '</style>')


def join_and_format_verses_to_html_tags(verses: list['VerseInfo']):
    out = []
    for group in group_sequential_verses(verses):
        first_verse, last_verse = group[0], group[-1]

        reference = f'{first_verse.book_name} {first_verse.chapter}:{first_verse.verse}'
        if first_verse.verse != last_verse.verse:
            reference += f'-{last_verse.verse}'

        verse_text = ' '.join(f'[V.{verse.verse}] {verse.text}' for verse in group)
        out.append(f"""
        <p class="verse_ref">{reference}</p>
        <br/>
        <p class="verse_text">{verse_text}</p>
        """)
    return '<br/>'.join(out)


def group_sequential_verses(verses: list['VerseInfo']):
    groupings = [[verses[0]]]
    for verse in verses[1:]:
        last_group = groupings[-1]
        last = last_group[-1]
        if verse.chapter == last.chapter and verse.verse == (last.verse + 1):
            last_group.append(verse)
        else:
            groupings.append([verse])
    return groupings


def format_verses_to_html(verses: list[VerseInfo]):
    header = f'''
    <head>
        {generate_css_style()}
    </head>
    <body>
        {join_and_format_verses_to_html_tags(verses)}
    </body>'''
    return HTML(header)


class RenderVerseCallableWrapper:
    def __call__(self, book, *verses):
        verse_data = get_verse(book, *verses)
        return format_verses_to_html(verse_data.verses)

    def __getitem__(self, item):
        book, verses = item[0], item[1:]
        return self(book, *verses)


render_verse = RenderVerseCallableWrapper()
