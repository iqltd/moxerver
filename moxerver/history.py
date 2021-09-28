from . import db
import json
import logging


class History(object):

    def __init__(self, api, reference):
        self.api = api
        self.reference = reference

    def get_data(self):
        SQL = "SELECT data FROM history WHERE app = ? and reference = ?"
        result = db.query_db(SQL, [self.api, self.reference], one=True)
        if result is None:
            return {}
        else:
            return json.loads(result["data"])


    def persist_data(self, data):
        logging.debug(f"Upserting {data} for {self.api}, {self.reference}")
        SQL = """INSERT INTO history (app, reference, data) VALUES (?, ?, ?)
                 ON CONFLICT(app, reference)
                 DO UPDATE SET data = excluded.data"""
        db.query_db(SQL, [self.api, self.reference, json.dumps(data)])
        db.get_db().commit()


class DummyHistory(History):

    def get_data(self):
        return {}

    def persist_data(self, _data):
        pass


def get_history(api, reference):
    if reference:
        return History(api, reference)
    return DummyHistory(api, reference)
