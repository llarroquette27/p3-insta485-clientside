"""Sample docstring."""
import hashlib
import flask
from flask import session
import insta485


def login_account(username, password):
    """Sample docstring."""
    connection = insta485.model.get_db()

    # Error checking
    if username == "" or password == "":
        flask.abort(400)

    if 'username' in session:
        flask.redirect('/')

    cur = connection.execute(
        "SELECT password FROM users "
        "WHERE username=? ",
        (username, )
    )

    real_password = cur.fetchone()
    if not real_password:
        flask.abort(403)

    real_password = real_password['password']
    salt = real_password.split('$')[1]

    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    if real_password != password_db_string:
        flask.abort(403)

    # Create session for user
    session['username'] = username
