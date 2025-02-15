"""Authenticate user."""
import hashlib
import flask
from flask import session
import insta485


def authentication():
    """Authenticate docstring."""
    # User authentication
    connection = insta485.model.get_db()

    if 'username' not in session:
        if not flask.request.authorization:
            flask.abort(403)

        real_password = connection.execute(
            "SELECT password FROM users "
            "WHERE username=? ",
            (flask.request.authorization['username'], )
        ).fetchone()

        if not real_password['password']:
            flask.abort(403)

        real_password = real_password['password']
        salt = real_password.split('$')[1]

        algorithm = 'sha512'
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + flask.request.authorization['password']
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])

        if password_db_string != real_password:
            flask.abort(403)

        session['username'] = flask.request.authorization['username']
