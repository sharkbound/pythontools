class ModifyID:
    SUMMARY_INPUT = 'summary##input'
    TAGS_INPUT = 'tags (comma separated)##input'
    ID_INPUT = 'record id##input'
    LOCATION_INPUT = 'location##input'

    LOAD_FROM_ID_BUTTON = 'load from id##button'
    SUMMARY_INPUT_SET_BUTTON = 'update summary##button##set'
    TAGS_INPUT_SET_BUTTON = 'update tags##button##set'
    LOCATION_INPUT_SET_BUTTON = 'update location##button##set'
    ADD_RECORD_BUTTON = 'add record##button##add##record'

    ERROR_TEXT = 'error status##error##text'


class FindID:
    FIND_BY_ID = 'find by id##input##int'
    FIND_BY_TAG = 'find by tag##input'
    FIND_BY_SUMMARY = 'find by summary##input'

    RECORD_ID = 'record id##readonly'
    SUMMARY = 'summary##findtab'
    TAGS = 'tags##findtab'
    READ_ONLY_LOCATION = 'location##readonly'

    RESULT_TABLE = 'search results##table'
