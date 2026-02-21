import pytest

from appname.models import db, get_or_none, transaction
from appname.models.user import User

create_user = True

@pytest.mark.usefixtures("testapp")
class TestModels:
    def test_user_save(self, testapp):
        """ Test Saving the user model to the database """

        user = User('user@example.com', 'supersafepassword')
        db.session.add(user)
        db.session.commit()

        user_obj = User.query.filter_by(email="user@example.com").first()
        assert user_obj is not None
        assert not user_obj.is_admin

    def test_user_password(self, testapp):
        """ Test password hashing and checking """
        admin = User('admin@example.com', 'supersafepassword', admin=True)

        assert admin.email == 'admin@example.com'
        assert admin.email == 'admin@example.com'
        assert admin.check_password('supersafepassword')
        assert admin.is_admin

    def test_user_group_creation(self, testapp):
        """ Test that creating a user, creates a group & a membership """
        user = User('user@example.com', 'supersafepassword')
        db.session.add(user)
        db.session.commit()
        assert len(user.memberships) == 1

    def test_user_encryption(self, testapp):
        """ Test that encryption works """
        user = User('user2@example.com', 'supersafepassword')
        secret = "baasdasdas"
        user.encrypted_totp_secret = secret
        db.session.add(user)
        db.session.commit()
        assert len(user.memberships) == 1
        assert User.query.all()[-1].encrypted_totp_secret == secret

    def test_get_or_none_respects_soft_delete(self, testapp):
        user = User('softdelete@example.com', 'supersafepassword')
        db.session.add(user)
        db.session.commit()

        user.deleted = True
        db.session.add(user)
        db.session.commit()

        assert get_or_none(User, user.id) is None
        assert get_or_none(User, user.id, with_deleted=True) is not None

    def test_query_with_deleted_can_fetch_deleted_rows(self, testapp):
        user = User('withdeleted@example.com', 'supersafepassword')
        db.session.add(user)
        db.session.commit()

        user.deleted = True
        db.session.add(user)
        db.session.commit()

        assert get_or_none(User, user.id) is None

        active_query = User.query
        with_deleted_query = User.query.with_deleted()
        assert active_query.get(user.id) is None
        assert with_deleted_query.get(user.id) is not None

    def test_query_with_deleted_requires_identifier(self, testapp):
        with pytest.raises(TypeError):
            User.query.with_deleted()._get()

    def test_model_serialization_and_delete_paths(self, testapp, monkeypatch):
        user = User('modelhelpers@example.com', 'supersafepassword')
        db.session.add(user)
        db.session.commit()

        as_dict = user.as_dict()
        assert as_dict["email"] == "modelhelpers@example.com"

        user.from_dict({"full_name": "Model Helper"})
        assert user.full_name == "Model Helper"

        user.delete(force=False)
        assert user.deleted is True

        monkeypatch.setattr(User, "can_be_destroyed", property(lambda _self: False))
        with pytest.raises(Exception):
            user.delete(force=True)

    def test_transaction_rolls_back_on_exception(self, testapp):
        user = User.lookup("user@example.com")
        original_name = user.full_name

        @transaction
        def update_and_fail():
            user.full_name = "Rollback Name"
            db.session.add(user)
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            update_and_fail()

        db.session.expire_all()
        assert User.lookup("user@example.com").full_name == original_name
