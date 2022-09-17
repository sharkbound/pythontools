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


@dataclass
class VerseRef:
    chapter: int
    start: int = -1
    end: int = -1


def build_api_url(book, verse: VerseRef):
    ext = ''
    if verse.start != -1:
        ext += f':{verse.start}'
    if verse.end != -1:
        ext += f'-{verse.end}'
    return f'{BASE_API}{book}+{verse.chapter}{ext}?translation=kjv'


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


def get_verse(book, verse: VerseRef):
    r = requests.get(url := build_api_url(book, verse))
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


def join_and_format_verses(verses: list['VerseInfo']):
    out = []
    for verse in verses:
        out.append(f' [V.{verse.verse}] {verse.text}')
    return ''.join(out)


def format_verse_to_html(verse_data: 'GetVerseResult'):
    joined_verses = join_and_format_verses(verse_data.verses)
    header = f'''
    <head>
        {generate_css_style()}
    </head>
    <body>
        <p class="verse_ref">{verse_data.reference}</p>
        <br/>
        <p class="verse_text">{joined_verses}</p>
    </body>'''
    return HTML(header)


def render_verse(book, verse: VerseRef):
    verse_data = get_verse(book, verse)
    return format_verse_to_html(verse_data)
