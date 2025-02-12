"""Delete a comment"""
import flask
from flask import session, request
import insta485
import hashlib


@insta485.app.route('/api/v1/comments/<int:commentid>/', methods=['DELETE'])
def delete_comment(commentid):
    """Delete a comment."""
    # User authentication
    connection = insta485.model.get_db()
    if 'username' not in session:
        print("No username in session")
        if not flask.request.authorization:
            flask.abort(403)
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']

        real_password = connection.execute(
            "SELECT password FROM users "
            "WHERE username=? ",
            (username, )
        ).fetchone()

        real_password = real_password['password']
        if not real_password:
            flask.abort(403)

        salt = real_password.split('$')[1]

        algorithm = 'sha512'
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])

        if password_db_string != real_password:
            flask.abort(403)

        session['username'] = username

    username = session['username']

    # Check if the comment exists
    comment = connection.execute(
        "SELECT * FROM comments "
        "WHERE commentid=?",
        (commentid, )
    ).fetchone()

    if not comment:
        flask.abort(404)

    # Check if the user owns the comment
    if comment['owner'] != username:
        flask.abort(403)

    # Delete the comment
    connection.execute(
        "DELETE FROM comments "
        "WHERE commentid=?",
        (commentid, )
    )

    connection.commit()

    return (request.url + str(commentid) + "/"), 204
    