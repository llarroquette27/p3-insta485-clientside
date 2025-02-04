"""Sample docstring."""

import hashlib
import uuid
import flask
from flask import session
import insta485


def update_password(password, new_password1, new_password2):
    """Sample docstring."""
    connection = insta485.model.get_db()

    # Update Password
    logname = session['username']
    if not logname:
        flask.abort(403)

    if (not password) or (not new_password1) or (not new_password2):
        flask.abort(400)

    # Verify password against the user’s password hash in the database.
    # If verification fails, abort(403).
    # Verify both new passwords match. If verification fails, abort(401).
    # Update hashed password entry in database.
    # See above for the password storage procedure.

    real_password = connection.execute(
        "SELECT password FROM users "
        "WHERE username=? ",
        (logname, )
    ).fetchone()

    if not real_password:
        flask.abort(403)

    real_password = real_password['password']
    salt = real_password.split('$')[1]

    hash_obj = hashlib.new('sha512')
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join(['sha512', salt, password_hash])

    if real_password != password_db_string:
        flask.abort(403)

    if new_password1 != new_password2:
        flask.abort(401)

    salt = uuid.uuid4().hex
    hash_obj = hashlib.new('sha512')
    new_password_salted = salt + new_password2
    hash_obj.update(new_password_salted.encode('utf-8'))
    new_password_hash = hash_obj.hexdigest()
    new_password_db_string = "$".join(['sha512', salt, new_password_hash])

    connection.execute(
        "UPDATE users "
        "SET password = ? "
        "WHERE username = ?",
        (new_password_db_string, logname, )
    )

    connection.commit()
