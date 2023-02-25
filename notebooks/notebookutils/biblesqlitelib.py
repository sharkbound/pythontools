import sqlite3
import typing

from pathlib import Path
from typing import NamedTuple

from IPython.core.display import HTML

RAW = 'raw'
JOIN = 'join'
VERSE_QUERY_TYPE = typing.Union[
    tuple[
        int,  # book
    ],
    tuple[
        int,  # book
        int,  # chapter
    ],
    tuple[
        int,  # book
        int,  # chapter
        int,  # verse
    ],
    tuple[
        int,  # book
        int,  # chapter
        int,  # verse
        Ellipsis  # verse to last verse of chapter
    ],
    tuple[
        int,  # book
        int,  # chapter
        Ellipsis,  # start to end verse
        int  # verse end
    ],
    tuple[
        int,  # book
        int,  # chapter
        int,  # verse start
        int,  # verse end
    ]
]


def _format_book_name(book_name: str):
    casefold_book_name = book_name.casefold()
    if 'first' in casefold_book_name:
        casefold_book_name = casefold_book_name.replace('first', '1')

    if 'second' in casefold_book_name:
        casefold_book_name = casefold_book_name.replace('second', '2')

    return ' '.join(s.capitalize() for s in casefold_book_name.split('_'))


INT_TO_BOOK_NAME = dict(zip(
    range(1, 67),
    (
        _format_book_name('GENESIS'), _format_book_name('EXODUS'), _format_book_name('LEVITICUS'),
        _format_book_name('NUMBERS'),
        _format_book_name('DEUTERONOMY'), _format_book_name('JOSHUA'), _format_book_name('JUDGES'),
        _format_book_name('RUTH'),
        _format_book_name('FIRST_SAMUEL'), _format_book_name('SECOND_SAMUEL'), _format_book_name('FIRST_KINGS'),
        _format_book_name('SECOND_KINGS'), _format_book_name('FIRST_CHRONICLES'),
        _format_book_name('SECOND_CHRONICLES'),
        _format_book_name('EZRA'), _format_book_name('NEHEMIAH'), _format_book_name('ESTHER'),
        _format_book_name('JOB'), _format_book_name('PSALMS'), _format_book_name('PROVERBS'),
        _format_book_name('ECCLESIASTES'),
        _format_book_name('SONG_OF_SONGS'), _format_book_name('ISAIAH'), _format_book_name('JEREMIAH'),
        _format_book_name('LAMENTATIONS'),
        _format_book_name('EZEKIEL'), _format_book_name('DANIEL'), _format_book_name('HOSEA'),
        _format_book_name('JOEL'), _format_book_name('AMOS'), _format_book_name('OBADIAH'), _format_book_name('JONAH'),
        _format_book_name('MICAH'), _format_book_name('NAHUM'),
        _format_book_name('HABAKKUK'), _format_book_name('ZEPHANIAH'), _format_book_name('HAGGAI'),
        _format_book_name('ZECHARIAH'),
        _format_book_name('MALACHI'), _format_book_name('MATTHEW'), _format_book_name('MARK'),
        _format_book_name('LUKE'),
        _format_book_name('JOHN'), _format_book_name('ACTS'), _format_book_name('ROMANS'),
        _format_book_name('FIRST_CORINTHIANS'),
        _format_book_name('SECOND_CORINTHIANS'), _format_book_name('GALATIANS'), _format_book_name('EPHESIANS'),
        _format_book_name('PHILIPPIANS'), _format_book_name('COLOSSIANS'),
        _format_book_name('FIRST_THESSALONIANS'), _format_book_name('SECOND_THESSALONIANS'),
        _format_book_name('FIRST_TIMOTHY'), _format_book_name('SECOND_TIMOTHY'), _format_book_name('TITUS'),
        _format_book_name('PHILEMON'), _format_book_name('HEBREWS'), _format_book_name('JAMES'),
        _format_book_name('FIRST_PETER'), _format_book_name('SECOND_PETER'), _format_book_name('FIRST_JOHN'),
        _format_book_name('SECOND_JOHN'),
        _format_book_name('THIRD_JOHN'), _format_book_name('JUDE'), _format_book_name('REVELATION')))
)

(
    GENESIS, EXODUS, LEVITICUS, NUMBERS, DEUTERONOMY, JOSHUA, JUDGES, RUTH, FIRST_SAMUEL, SECOND_SAMUEL, FIRST_KINGS,
    SECOND_KINGS, FIRST_CHRONICLES, SECOND_CHRONICLES, EZRA, NEHEMIAH, ESTHER, JOB, PSALMS, PROVERBS, ECCLESIASTES,
    SONG_OF_Songs, ISAIAH, JEREMIAH, LAMENTATIONS, EZEKIEL, DANIEL, HOSEA, JOEL, AMOS, OBADIAH, JONAH, MICAH, NAHUM,
    HABAKKUK, ZEPHANIAH, HAGGAI, ZECHARIAH, MALACHI, MATTHEW, MARK, LUKE, JOHN, ACTS, ROMANS, FIRST_CORINTHIANS,
    SECOND_CORINTHIANS, GALATIANS, EPHESIANS, PHILIPPIANS, COLOSSIANS, FIRST_THESSALONIANS, SECOND_THESSALONIANS,
    FIRST_TIMOTHY, SECOND_TIMOTHY, TITUS, PHILEMON, HEBREWS, JAMES, FIRST_PETER, SECOND_PETER, FIRST_JOHN, SECOND_JOHN,
    THIRD_JOHN, JUDE, REVELATION) = range(1, 67)


class QueryVerseResult(NamedTuple):
    id: int
    book: int
    chapter: int
    verse: int
    text: str

    @property
    def reference(self):
        return f'{self.book_name} {self.chapter}:{self.verse}'

    @property
    def book_name(self) -> str:
        return INT_TO_BOOK_NAME[self.book]


class BibleVerseDB:
    # download the sqlite database from here: https://www.biblesupersearch.com/bible-downloads/
    def __init__(self, db_path: str | Path):
        if not isinstance(db_path, Path):
            db_path = Path(db_path)

        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)

    def cursor(self):
        return self.conn.cursor()

    def _query_cast(self, raw_query: str, **query_kv) -> list[QueryVerseResult]:
        cursor = self.cursor()
        cursor.execute(raw_query, query_kv)
        return [QueryVerseResult(*result) for result in cursor]

    def _find_last_verse_in_chapter(self, book: int, chapter: int, start_verse: int):
        res = self._query_cast('select * from verses where book = :book and chapter = :chapter and verse >= :start_verse order by verse desc limit 1',
                               book=book, chapter=chapter, start_verse=start_verse)

        if not res:
            return start_verse

        return res[0].verse

    def _replace_ellipsis(self, verse_ref: VERSE_QUERY_TYPE) -> VERSE_QUERY_TYPE:
        if len(verse_ref) != 4 or not any(v == Ellipsis for v in verse_ref):
            return verse_ref

        if verse_ref[-1] == Ellipsis:
            return (*verse_ref[:-1], self._find_last_verse_in_chapter(verse_ref[0], verse_ref[1], verse_ref[2]))

        elif verse_ref[-2] == Ellipsis:
            return (verse_ref[0], verse_ref[1], 1, verse_ref[3])

    def _build_query_for_verse_ref_tuple(self, verse_ref: VERSE_QUERY_TYPE):
        verse_ref = self._replace_ellipsis(verse_ref)

        match verse_ref:
            case (int() as book, ):
                filterquery = 'book = :book'
                filterdict = {'book': book}

            case (int() as book, int() as chapter):
                filterquery = 'book = :book and chapter = :chapter'
                filterdict = {'book': book, 'chapter': chapter}

            case (int() as book, int() as chapter, int() as verse):
                filterquery = 'book = :book and chapter = :chapter and verse = :verse'
                filterdict = {'book': book, 'chapter': chapter, 'verse': verse}

            case (int() as book, int() as chapter, int() as verse_start, int() as verse_end):
                filterquery = 'book = :book and chapter = :chapter and verse >= :verse_start and verse <= :verse_end'
                filterdict = {'book': book, 'chapter': chapter, 'verse_start': verse_start, 'verse_end': verse_end}

            case _:
                raise ValueError(f'invalid input for verse reference: {verse_ref}')

        return f'select * from verses where {filterquery}', filterdict

    def get(self, *verses: VERSE_QUERY_TYPE) -> list[QueryVerseResult]:
        verses_list = []
        for verse in verses:
            query, kwargs = self._build_query_for_verse_ref_tuple(verse)
            if ret := self._query_cast(query, **kwargs):
                verses_list.extend(ret)

        verses_list.sort(key=lambda x: (x.book, x.chapter, x.verse))
        return verses_list


def remove_duplicate_verses(verses: list['QueryVerseResult']):
    seen = set()
    non_duplicate_verses = []
    for verse in verses:
        if verse.id not in seen:
            non_duplicate_verses.append(verse)
            seen.add(verse.id)
    return non_duplicate_verses


def group_sequential_verses(verses: list['QueryVerseResult']):
    non_duplicate_verses = remove_duplicate_verses(verses)
    groupings = [[non_duplicate_verses[0]]]
    for verse in non_duplicate_verses[1:]:
        last_group = groupings[-1]
        last = last_group[-1]
        if verse.chapter == last.chapter and verse.verse == (last.verse + 1):
            last_group.append(verse)
        else:
            groupings.append([verse])
    return groupings


def create_biblegateway_link(ref: list):
    url = 'https://www.biblegateway.com/passage/?search={book_name}+{chapter}%3A{verse_start}{verse_end}&version=NIV'
    match ref:
        case [str() as book_name, int() as chapter]:
            return url.format(book_name=book_name, chapter=chapter, verse_start='', verse_end='')
        case [str() as book_name, int() as chapter, int() as verse_start]:
            return url.format(book_name=book_name, chapter=chapter, verse_start=verse_start, verse_end='')
        case [str() as book_name, int() as chapter, int() as verse_start, int() as verse_end]:
            return url.format(book_name=book_name, chapter=chapter, verse_start=verse_start, verse_end=f'-{verse_end}')
    raise ValueError(f'invalid format for verse ref: {ref!r}')


def join_and_format_verses_to_html_tags(verses: list['QueryVerseResult']):
    out = []
    for group in group_sequential_verses(verses):
        first_verse, last_verse = group[0], group[-1]

        reference = f'{first_verse.book_name} {first_verse.chapter}:{first_verse.verse}'
        ref_parts = [first_verse.book_name, first_verse.chapter, first_verse.verse]
        if first_verse.verse != last_verse.verse:
            reference += f'-{last_verse.verse}'
            ref_parts.append(last_verse.verse)

        verse_text = ' '.join(f'[V.{verse.verse}] {verse.text}' for verse in group)
        out.append(f"""
        <p class="verse_ref">{reference} <a href="{create_biblegateway_link(ref_parts)}">[NIV]</a></p>
        <br/>
        <p class="verse_text">{verse_text}</p>
        """)
    return '<br/>'.join(out)


def format_verses_to_html(verses: list[QueryVerseResult]):
    return join_and_format_verses_to_html_tags(verses)


def generate_css_style():
    return ('<style>'
            + '''
.verse_ref {
    font-size: 3em;
    font-family: Baskerville, serif;

}

.verse_text {
    font-size: 2.3em;
    font-family: Baskerville, serif;
    font-weight: normal;
}'''
            + '</style>')


DB = BibleVerseDB(r'D:\HddDownloads\world_english_bible.sqlite')


def render(*verses: VERSE_QUERY_TYPE, mode=RAW):
    if mode not in (RAW, JOIN):
        raise ValueError(f'invalid mode: {mode!r}, must be either [{RAW!r} or {HTML!r}]')
    
    render_verses = []
    if mode == RAW:
        for verseref in verses:
            render_verses.append(DB.get(verseref))
    else:
        items = []
        for verseref in verses:
            for verse in DB.get(verseref):
                items.append(verse)
        render_verses.append(items)
            
    output_verse_html = '\n'.join(format_verses_to_html(group) for group in render_verses)
            
    header = f'''
    <head>
        {generate_css_style()}
    </head>
    <body>
        {output_verse_html}
    </body>'''
    return HTML(header)


def samebook(book: int, *verses: VERSE_QUERY_TYPE):
    for verse in verses:
        yield (book, *verse)

# download the sqlite database from here: https://www.biblesupersearch.com/bible-downloads/
# print([it.reference for it in BibleVerseDB(r"D:\HddDownloads\world_english_bible.sqlite").get((DANIEL, 5, 1), (DANIEL, 1, 1))])
