from .event import Event

class Org():

    def __init__(self, config):
        self.__sync_list = config['sync']

    def __get_title(self, node):
        title = ''
        if node.todo is not None:
            title += node.todo + ' '
        title += str(node.heading)

        return title

    @classmethod
    def get_id(cls, desc):
        from orgparse import loads
        root = loads(desc)
        node = root.children[0]
        return node.get_property('ID')


    def get_ids(self, events):
        ids = []
        for event in events.values():
            desc = event['description']
            ids.append(self.get_id(desc))
        return ids

    def get_events(self):
        from orgparse import load

        events = {}
        for sync_info in self.__sync_list:
            root = load(sync_info['org_file'])

            for node in root[1:]:
                sched_event = self.__to_event(sync_info['calendar_id'], node, node.scheduled, id_prefix='S-')
                if sched_event is None:
                    continue
                events[sched_event.get_org_id()] = sched_event

            for node in root[1:]:
                deadline_event = self.__to_event(sync_info['calendar_id'], node, node.deadline,
                                                id_prefix='D-', title_prefix='締切 : ')
                if deadline_event is None:
                    continue
                events[deadline_event.get_org_id()] = deadline_event

        return events

    def __to_str(self, time):
        import pytz

        jst = pytz.timezone('Japan')
        time = jst.localize(time)  # 9:19ズレを修正した時差の追加方法

        return time.isoformat()

    def __pretty_body(self, body):
        import re

        # ヘッダーが無いと calendar から cal_id の取得時に orgparse がエラーを出す
        # # remove head line
        # nl = body.find('\n')
        # body = body[nl+1:] 

        # remove indent
        body = re.sub('\n *', '\n', body) 

        # add new line after :END:
        body = re.sub(':END:\n', ':END:\n\n', body)

        return body

    def __get_id(self, node, id_prefix=''):
        return id_prefix + node.get_property('ID')

    def __get_description(self, node, id_prefix=''):
        from orger import inorganic
        properties = {}
        properties['ID'] = self.__get_id(node, id_prefix)

        org_node = inorganic.node(
            heading = node.heading,
            body = node.body,
            properties = properties
        )
        body = org_node.render()
        return self.__pretty_body(body)

    def __to_event(self, calendar_id, node, time, id_prefix='', title_prefix=''):
        if time.start is None:
            return None

        if node.get_property('ID') is None:
            print('Warning: "%s" ID Undefined. skip uploading.' % self.__get_title(node))
            return None

        # case 1. <2020-05-09 Sat 15:00>             : OK
        # case 2. <2020-05-09 Sat 15:00-16:00>       : OK
        # case 3. <2020-05-09 Sat>                   : OK
        # case 4. <2020-05-09 Sat>--<2020-05-13 Wed> : orgparse 未対応 case 3 扱い

        # startとendでdateTimeまたはdateに揃える
        if time.has_time():
            date_key = 'dateTime'
            to_str = self.__to_str
        else:
            date_key = 'date'
            to_str = str

        event = Event(
            start=to_str(time.start),
            title=title_prefix + self.__get_title(node),
            description=self.__get_description(node, id_prefix),
            org_id=self.__get_id(node, id_prefix),
            calendar_id = calendar_id,
            end=to_str(time.start) if time.end is None else to_str(time.end)
        )

        return event
