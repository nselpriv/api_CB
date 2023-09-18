import pytest

from zeeguu.api.app import create_app
import zeeguu


@pytest.fixture
def client():
    app = create_app(testing=True)

    with app.test_client() as client:
        with app.app_context():
            zeeguu.core.model.db.create_all()

        yield client

    with app.app_context():
        zeeguu.core.model.db.session.remove()
        zeeguu.core.model.db.drop_all()


@pytest.fixture
def test_app():
    app = create_app(testing=True)

    with app.app_context():
        zeeguu.core.model.db.create_all()

        yield app

    with app.app_context():
        zeeguu.core.model.db.session.remove()
        zeeguu.core.model.db.drop_all()


@pytest.fixture
def client_with_new_user_and_session():
    app = create_app(testing=True)

    with app.test_client() as client:
        with app.app_context():
            zeeguu.core.model.db.create_all()

            # Creating a user and returning also the session
            test_user_data = dict(
                password="test", username="test", learned_language="de"
            )
            response = client.post(f"/add_user/test@test.es", data=test_user_data)
            assert response.status_code == 200

            session = int(response.data)

            def append_session(url):
                return url + "?session=" + str(session)

        yield client, session, append_session

    with app.app_context():
        zeeguu.core.model.db.session.remove()
        zeeguu.core.model.db.drop_all()