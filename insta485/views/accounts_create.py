"""Sample docstring."""

import uuid
import hashlib
import pathlib
import flask
from flask import session
import insta485


def create_account(username, password, fullname, email, user_file):
    """Sample docstring."""
    if 'username' in session:
        flask.redirect('/accounts/edit/')

    connection = insta485.model.get_db()
    if (not username) or (not password) or (not fullname):
        flask.abort(400)
    elif (not email) or (not user_file):
        flask.abort(400)
    # Check if username already exists
    cur = connection.execute(
        "SELECT * FROM users "
        "WHERE username = ?",
        (username, )
    )
    repeated_user = cur.fetchone()

    if repeated_user:
        print("User already exists")
        flask.abort(409)
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new('sha512')
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_db_string = "$".join(['sha512', salt, hash_obj.hexdigest()])
    # print(password_db_string)

    # Unpack flask object

    # Compute base name (filename without directory).
    # We use a UUID to avoid
    # clashes with existing files,
    # and ensure that the name is compatible with the
    # filesystem. For best practive,
    # we ensure uniform file extensions (e.g.
    # lowercase).
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(user_file.filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"

    # Save to disk
    user_file.save(insta485.app.config["UPLOAD_FOLDER"]/uuid_basename)

    # log user in and redirect to URL
    # look into database to see if user exists

    connection.execute(
        "INSERT INTO users (username, password, fullname, "
        "email, filename) "
        "VALUES (?, ?, ?, ?, ?)",
        (username, password_db_string, fullname, email, uuid_basename, )
    )

    connection.commit()
    session['username'] = username
