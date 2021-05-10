import datetime
from datetime import timedelta

from dateutil.utils import today

import zeeguu_core

import flask
from flask import jsonify
from sqlalchemy.orm.exc import NoResultFound

from zeeguu_core.model import User, Cohort
from zeeguu_core.user_statistics.exercise_corectness import exercise_correctness
from .decorator import only_teachers
from .helpers import student_info_for_teacher_dashboard
from .permissions import (
    check_permission_for_cohort,
    check_permission_for_user,
)
from .. import api
from ..utils.json_result import json_result
from ..utils.route_wrappers import with_session

db = zeeguu_core.db


@api.route("/user_info/<id>/<duration>", methods=["GET"])
@with_session
def user_info_api(id, duration):

    check_permission_for_user(id)

    return jsonify(student_info_for_teacher_dashboard(id, duration))


@api.route("/cohort_member_bookmarks/<id>/<time_period>", methods=["GET"])
@with_session
@only_teachers
def cohort_member_bookmarks(id, time_period):

    user = User.query.filter_by(id=id).one()

    check_permission_for_cohort(user.cohort_id)

    now = datetime.today()
    date = now - timedelta(days=int(time_period))

    cohort_language_id = Cohort.query.filter_by(id=user.cohort_id).one().language_id

    # True input causes function to return context too.
    return json_result(
        user.bookmarks_by_day(
            True, date, with_title=True, max=10000, language_id=cohort_language_id
        )
    )


@api.route("/cohort_member_reading_sessions/<id>/<time_period>", methods=["GET"])
@with_session
def cohort_member_reading_sessions(id, time_period):
    """
    Returns reading sessions from member with input user id.
    """
    try:
        user = User.query.filter_by(id=id).one()
    except NoResultFound:
        flask.abort(400)
        return "NoUserFound"

    check_permission_for_cohort(user.cohort_id)

    cohort = Cohort.query.filter_by(id=user.cohort_id).one()
    cohort_language_id = cohort.language_id

    now = today()
    date = now - timedelta(days=int(time_period))
    return json_result(
        user.reading_sessions_by_day(date, max=10000, language_id=cohort_language_id)
    )


@api.route("/student_exercise_correctness", methods=["POST"])
@with_session
def student_exercise_correctness():
    """
    e.g. POST http://localhost:9001/exercise_correctness/534/30
        {
            "Correct": 55,
            "2nd Try": 55,
            "Incorrect": 4,
            "too_easy": 1,
            "Bad Example":1,
        }
    :param student_id: int
    :param number_of_days: int
    :param cohort_id: int
    :return:
    """

    student_id = flask.request.form.get("student_id")
    number_of_days = flask.request.form.get("number_of_days")
    cohort_id = flask.request.form.get("cohort_id")

    try:
        user = User.query.filter_by(id=student_id).one()
    except NoResultFound:
        flask.abort(400)

    # check_permission_for_user(user.id)

    now = today()
    then = now - timedelta(days=int(number_of_days))
    stats = exercise_correctness(user.id, cohort_id, then, now)

    return json_result(stats)
