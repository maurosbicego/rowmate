from fastapi import Depends, APIRouter, HTTPException
from bson.binary import Binary
from datetime import datetime
from uuid import UUID

import pymongo

# models
from models.event import Event, UpdateEvent
from models.calendar import Calendar

# utils
from utils.interval import generate_interval
from utils.uuid import generate_uuid


def get_events_router(database, authenticator) -> APIRouter:
    router = APIRouter()

    @router.get('/{lang}')
    async def get_all_events(lang, user=Depends(
            authenticator.get_current_active_user)):
        query = {'event_time': {'$gte': datetime.utcnow()}}
        sort = [('event_time', pymongo.ASCENDING)]

        filter = {'_id': True,
                  f'titles.{lang}.title': True,
                  f'descriptions.{lang}.description': True,
                  'max_participants': True,
                  'min_participants': True,
                  'repeat_interval': True,
                  'contact_person': True,
                  'repeat_unit': True,
                  'modified_at': True,
                  'created_at': True,
                  'event_time': True,
                  'start_time': True,
                  'end_time': True,
                  'location': True}

        res = await database['events'].find(
            query, filter).sort(sort).to_list(length=150)

        if len(res) > 0:
            return res
        else:
            raise HTTPException(status_code=404, detail='No events were found')

    return router


def get_event_router(database, authenticator) -> APIRouter:
    router = APIRouter()

    @router.get('/latest')
    async def get_latest_event(user=Depends(authenticator.get_current_active_user)):
        sort = [('created_at', pymongo.DESCENDING)]
        res = await database['events'].find().sort(sort).to_list(length=1)

        if len(res) > 0:
            return res[0]
        else:
            raise HTTPException(status_code=404, detail='Event was not found')

    @router.post('/')
    async def post_event(request: Event,
                         user=Depends(authenticator.get_current_superuser)):
        event_times = generate_interval(request)
        request_doc = dict(request)
        inserted = []

        for event_time in event_times:
            uuid: Binary = generate_uuid()
            created_at: datetime = datetime.utcnow()

            event_doc: Event = {
                '_id': uuid,
                'author': user.name,
                'created_at': created_at,
                'event_time': event_time,
                'titles': request_doc['titles'],
                'location': request_doc['location'],
                'repeat_unit': request_doc['repeat_unit'],
                'descriptions': request_doc['descriptions'],
                'repeat_interval': request_doc['repeat_interval'],
                'min_participants': request_doc['min_participants'],
                'max_participants': request_doc['max_participants'],
                'contact_person': request_doc['contact_person'],
                'start_time': request_doc['start_time'],
                'end_time': request_doc['end_time']
            }

            res = await database['events'].insert_one(event_doc)

            if res.acknowledged:
                inserted.append(res.inserted_id)

        uuid: Binary = generate_uuid()

        calendar_doc: Calendar = {
            '_id': uuid,
            'events': inserted,
            'start_time': request_doc['start_time'],
            'end_time': request_doc['end_time']
        }

        res = await database['calendars'].insert_one(calendar_doc)

        if res.acknowledged:
            return {'detail': 'Events successfully created'}
        else:
            raise HTTPException(
                status_code=400, detail='Error creating calendar')

    @router.patch('/{hex}')
    async def patch_event(hex: str,
                          request: UpdateEvent,
                          user=Depends(authenticator.get_current_superuser)):
        try:
            req_uuid = UUID(hex=hex, version=4)
        except TypeError:
            raise HTTPException(status_code=404, detail='Event was not found')

        query = {'events': {'$in': [req_uuid]}}
        res = await database['calendars'].find(query).to_list(length=1)

        if len(res) == 0:
            raise HTTPException(
                status_code=404, detail='Calender was not found')

        updated = []
        inserted = []
        deleted = []

        event_times = generate_interval(request)
        existing_events = len(res[0]['events'])
        interval_events = len(event_times)

        for event_time_index, event_time in enumerate(event_times):
            modified_at: datetime = datetime.utcnow()
            request_doc = dict(request)

            event_doc: Event = {
                'event_time': event_time,
                'titles': request_doc['titles'],
                'location': request_doc['location'],
                'repeat_unit': request_doc['repeat_unit'],
                'descriptions': request_doc['descriptions'],
                'repeat_interval': request_doc['repeat_interval'],
                'min_participants': request_doc['min_participants'],
                'max_participants': request_doc['max_participants'],
                'contact_person': request_doc['contact_person'],
                'start_time': request_doc['start_time'],
                'end_time': request_doc['end_time']
            }

            if existing_events > 0:
                event_doc['modified_by'] = user.name
                event_doc['modified_at'] = modified_at

                document = {'$set': event_doc}
                query = {'_id': {'$in': [res[0]['events'][event_time_index]]}}

                update_res = await database['events'].update_many(query, document)

                if update_res.acknowledged:
                    updated.append(res[0]['events'][event_time_index])
            elif existing_events < 0 and existing_events < interval_events:
                created_at: datetime = datetime.utcnow()
                uuid: Binary = generate_uuid()

                event_doc['_id'] = uuid
                event_doc['author'] = user.name
                event_doc['created_at'] = created_at

                insert_res = await database['events'].insert_one(event_doc)

                if insert_res.acknowledged:
                    inserted.append(insert_res.inserted_id)

            existing_events = existing_events - 1
        interval_events = interval_events - 1

        delete_uuids = set(res[0]['events']) - set(updated)

        if len(delete_uuids) > 0:
            for uuid in delete_uuids:
                query = {'_id': uuid}

                delete_res = await database['events'].delete_one(query)

                if delete_res.deleted_count > 0:
                    deleted.append(uuid)

        if len(inserted) > 0:
            calendar_doc: Calendar = {
                'start_time': request_doc['start_time'],
                'end_time': request_doc['end_time']
            }

            query = {'events': {'$in': [req_uuid]}}
            document = {'$set': calendar_doc,
                        '$addToSet': {'events': {'$each': inserted}}}

            await database['calendars'].update_one(query, document)

        if len(updated) > 0:
            calendar_doc: Calendar = {
                'start_time': request_doc['start_time'],
                'end_time': request_doc['end_time']
            }

            query = {'events': {'$in': [req_uuid]}}
            document = {'$set': calendar_doc}

            await database['calendars'].update_one(query, document)

        if len(deleted) > 0:
            calendar_doc: Calendar = {
                'start_time': request_doc['start_time'],
                'end_time': request_doc['end_time']
            }

            query = {'events': {'$in': [req_uuid]}}
            document = {'$pullAll': {'events': deleted}}

            await database['calendars'].update_one(query, document)

        if len(updated) > 0 or len(inserted) > 0 or len(deleted) > 0:
            return {'updated': len(updated),
                    'inserted': len(inserted),
                    'deleted': len(deleted)}
        else:
            raise HTTPException(status_code=400, detail='Calendar not updated')

    return router