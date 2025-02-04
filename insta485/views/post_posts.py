"""Sample docstring."""
import pathlib
import uuid
import os
import flask
import insta485

# POST /posts/?target=URL
# This endpoint only accepts POST requests.
# Create or delete a post and immediately redirect to URL


LOGGER = flask.logging.create_logger(insta485.app)


@insta485.app.route('/posts/', methods=['POST'])
def post_post():
    """Sample docstring."""
    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')
    logname = flask.session['username']

    target = flask.request.args.get('target', f"/users/{logname}/")
    LOGGER.debug("target = %s", target)

    operation = flask.request.form["operation"]

    connection = insta485.model.get_db()

    if operation == "create":
        # Unpack flask object
        fileobj = flask.request.files["file"]
        filename = fileobj.filename

        # Error check
        if filename == "":
            flask.abort(400)

        # Compute base name (filename without directory).
        # We use a UUID to avoid
        # clashes with existing files, and ensure that the
        # name is compatible with the
        # filesystem. For best practive, we ensure uniform
        # file extensions (e.g.
        # lowercase).
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"

        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)

        connection.execute(
            "INSERT INTO posts (filename, owner ) "
            "VALUES (?, ?) ",
            (uuid_basename, logname, )
        )
    else:
        # delete image from filestream and database
        postid = flask.request.form['postid']

        # Get filename
        cur = connection.execute(
            "SELECT * FROM posts "
            "WHERE postid=? ",
            (postid, )
        )
        post = cur.fetchone()
        filename = post['filename']

        # Error check
        if post['owner'] != logname:
            flask.abort(403)

        filepath = insta485.app.config["UPLOAD_FOLDER"] / filename
        if os.path.exists(filepath):
            os.remove(filepath)

        connection.execute(
            "DELETE FROM posts "
            "WHERE postid=? ",
            (postid, )
        )

    connection.commit()
    return flask.redirect(target)
