"""Sample docstring."""
import uuid
import pathlib
import os
import flask
from flask import session
import insta485


def edit_account(fullname, email, user_file):
    """Sample docstring."""
    connection = insta485.model.get_db()

    # Edit account
    logname = session['username']

    # if user is not logged in, return 403
    if not logname:
        flask.abort(403)

    fullname = flask.request.form["fullname"]
    email = flask.request.form["email"]
    user_file = flask.request.files["file"]

    if (not email) or (not fullname):
        flask.abort(400)

    if not user_file:
        # only update email and fullname
        connection.execute(
            "UPDATE users "
            "SET fullname = ?, email = ? "
            "WHERE username = ?",
            (fullname, email, logname, )
        )

        connection.commit()

    else:

        # if a photo is included, the server will update the user's
        # picture, name and email.
        # Delete the old photo from the file system.
        filename = user_file.filename

        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"

        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        user_file.save(path)

        # Get filename
        cur = connection.execute(
            "SELECT filename FROM users "
            "WHERE username=? ",
            (logname, )
        )
        profile_pic = cur.fetchone()["filename"]

        connection.execute(
            "UPDATE users "
            "SET fullname = ?, email = ?, filename = ? "
            "WHERE username = ?",
            (fullname, email, uuid_basename, logname, )
        )

        filepath = insta485.app.config["UPLOAD_FOLDER"] / profile_pic
        if os.path.exists(filepath):
            os.remove(filepath)

        connection.commit()
