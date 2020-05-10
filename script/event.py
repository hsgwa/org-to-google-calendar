
class Event():
    def __init__(self, title, description, start, org_id, calendar_id, end=None, event_id=None):
        self.__title = title
        self.__description = description
        self.__start = start
        self.__org_id = org_id
        self.__end = end
        self.__event_id = event_id
        self.__time_zone = 'Asia/Tokyo'
        self.__has_time = self.is_iso8601(start)
        self.__calendar_id = calendar_id

    @classmethod
    def is_same(cls, event, event_):
        return event.get_title()       == event_.get_title()       and \
               event.get_description() == event_.get_description() and \
               event.get_start()       == event_.get_start()       and \
               event.get_end()         == event_.get_end()

    @classmethod
    def is_iso8601(cls, str_val):
        import re
        # ref. https://stackoverflow.com/questions/41129921/validate-an-iso-8601-datetime-string-in-python
        regex = '^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'

        if not hasattr(cls, '__match_iso8601'):
            cls.__match_iso8601 = re.compile(regex).match

        try:
            if cls.__match_iso8601(str_val) is not None:
                return True
        except:
            pass

        return False

    def get_title(self):
        return self.__title

    def get_description(self):
        return self.__description

    def get_start(self):
        return self.__start

    def get_org_id(self):
        return self.__org_id

    def get_end(self):
        return self.__end

    def get_event_id(self):
        return self.__event_id

    def get_calendar_id(self):
        return self.__calendar_id

    def get_body(self):
        body = {}
        body['summary'] = self.__title
        body['description'] = self.__description
        body['start'] = {}
        body['end'] = {}
        body['start']['timeZone'] = self.__time_zone
        body['end']['timeZone'] = self.__time_zone

        if self.__has_time:
            date_key = 'dateTime'
        else:
            date_key = 'date'

        body['start'][date_key] = self.__start
        body['end'][date_key] = self.__start

        return body
