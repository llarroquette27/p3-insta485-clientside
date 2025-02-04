"""Sample docstring."""

import flask
from flask import session
import insta485


def delete_account():
    """Delete the user's account, removes associated data from the database."""
    connection = insta485.model.get_db()

    if 'username' not in flask.session:
        flask.abort(403)

    user = session['username']

    # Delete everything from database
    # connection.execute(
    #     "DELETE FROM users "
    #     "WHERE username=? ",
    #     (user, )
    # )
    # connection.commit()
    # Delete all post files created by this user. Delete user icon file.
    # Delete all related entries in all tables.
    # since databses are set up properly and have foreign key constraints,
    # deleting the user will delete all related entries in all tables
    connection.execute(
        "DELETE FROM users "
        "WHERE username=? ",
        (user, )
    )
    connection.commit()

    # Clear session
    session.clear()
