from .event import Event
from .org import Org

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path

SCOPES = ['https://www.googleapis.com/auth/calendar']

class Calendar():
    def __init__(self, config):
        self.__sync_list = config['sync']
        self.__token = config['generate_token']
        self.__client_secret = config['client_secret']
        self.__update_cred()

    def insert(self, event):
        response = self.__service.events().insert(
            calendarId=event.get_calendar_id(),
            body=event.get_body()
        ).execute()

    def get_events(self):
        events = {}

        for sync_info in self.__sync_list:
            response = self.__service.events().list(
                calendarId=sync_info['calendar_id'],
                singleEvents=True
            ).execute()

            for body in response.get('items', []):
                if 'description' not in body :
                    raise ValueError("calendar event has no description. clear calendar events.")
                desc = body['description']
                events[Org.get_id(desc)] = self.__to_event(body)

        return events

    def clear_events(self, desc=''):
        # TODO: reccurring events の削除に対応

        for sync_info in self.__sync_list:
            response = self.__service.events().list(
                calendarId=sync_info['calendar_id'],
                singleEvents=True
            ).execute()

            for body in response.get('items', []):
                self.__delete(sync_info['calendar_id'], body['id'])
                print('Event deleted : {} '.format(body['summary']))

    def __delete(self,  calendar_id, event_id):
        self.__service.events().delete(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()

    def delete(self,  event):
        self.__delete(event.get_calendar_id(), event.get_event_id())

    def update(self, to_event, from_event):
        self.__service.events().update(
            calendarId=to_event.get_calendar_id(),
            eventId=to_event.get_event_id(),
            body=from_event.get_body()
        ).execute()

    def __update_cred(self):
        creds = None

        if os.path.exists(self.__token):
            with open(self.__token, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.__client_secret, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(self.__token, 'wb') as token:
                pickle.dump(creds, token)

        self.__service = build('calendar', 'v3', credentials=creds)

    def __to_event(self, json):
        has_time = 'dateTime' in json['start']

        if has_time :
            time_key = 'dateTime'
        else:
            time_key = 'date'

        event = Event(
            start=json['start'][time_key],
            title=json['summary'],
            description=json['description'],
            org_id=Org.get_id(json['description']),
            calendar_id=json['organizer']['email'],
            end=json['end'][time_key],
            event_id=json['id']
        )

        return event
