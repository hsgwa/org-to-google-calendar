from .calendar import Calendar
from .org import Org
from .event import Event

class EventManager():
    def __init__(self, config):
        self.__org = Org(config)
        self.__cal = Calendar(config)

    def clear(self):
        from tqdm import tqdm

        events = self.__cal.get_events()

        pbar = tqdm(total=len(events), desc='[Deleting all events...] ')
        for i, event in enumerate(events.values()):
            pbar.set_description('[Delete events {}/{}] '.format(i, len(events)))
            self.__cal.delete(event)
            pbar.update(1)
        pbar.close()

        print('%s events deleted.' % len(events))

    def update(self):
        from tqdm import tqdm

        org_events = self.__org.get_events()
        cal_events = self.__cal.get_events()

        org_id_set = set(org_events.keys())
        cal_id_set = set(cal_events.keys())

        delete_ids = list(cal_id_set - org_id_set)
        add_ids    = list(org_id_set - cal_id_set)
        update_ids = list(cal_id_set & org_id_set)
        update_ids = self.__exclude_same(org_events, cal_events, update_ids)

        pbar = tqdm(total=len(add_ids)+len(delete_ids)+len(update_ids))

        for i, key in enumerate(add_ids):
            self.__cal.insert(org_events[key])
            pbar.update(1)
            pbar.set_description('[Add events {}/{}] '.format(i, len(add_ids)))

        for i, key in enumerate(delete_ids):
            self.__cal.delete(cal_events[key])
            pbar.update(1)
            pbar.set_description('[Delete events {}/{}] '.format(i, len(delete_ids)))

        for i, key in enumerate(update_ids):
            self.__cal.update(cal_events[key], org_events[key])
            pbar.set_description('[Update events {}/{}] '.format(i, len(update_ids)))
            pbar.update(1)

        pbar.close()

        print('org->google calendar sync succeed.')

        if len(add_ids) > 0:
            print('%s events added.' % len(add_ids))
        if len(delete_ids) > 0:
            print('%s events deleted.' % len(delete_ids))
        if len(update_ids) > 0:
            print('%s events updated.' % len(update_ids))

    def __exclude_same(self, events, events_, org_ids):
        update_ids = []
        for org_id in org_ids:
            if Event.is_same(events[org_id], events_[org_id]):
                continue
            update_ids.append(org_id)
        return update_ids
