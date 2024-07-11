import datetime
import uuid

from sqlalchemy.orm.exc import NoResultFound

from zeeguu.core.model.user import User

from zeeguu.core.model import db


class Session(db.Model):
    __table_args__ = {"mysql_collate": "utf8_bin"}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)
    last_use = db.Column(db.DateTime)
    uuid = db.Column(db.String(36), unique=True, nullable=False)

    def __init__(self, user, _uuid: str):
        self.uuid = _uuid
        self.user = user
        self.update_use_date()

    def update_use_date(self):
        self.last_use = datetime.datetime.now()

    @classmethod
    def create_for_user(cls, user):

        _uuid = uuid.uuid4().hex
        while True:
            if cls.query.get(_uuid) is None:
                break
            _uuid = uuid.uuid4().hex
        return cls(user, _uuid)

    @classmethod
    def find(cls, _uuid: str = None):
        # gets the session object for a given uuid

        try:
            object_from_db = cls.query.filter(cls.uuid == _uuid).one()

            return object_from_db
        except NoResultFound:
            return None
