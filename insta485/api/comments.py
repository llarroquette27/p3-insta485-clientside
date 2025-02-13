"""Add one comment to a post."""
import flask
from flask import session, request
import insta485
import hashlib


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def post_comments():
    """Sample docstring."""
    # User authentication
    connection = insta485.model.get_db()
    if 'username' not in session:
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

    postid = request.args.get('postid')
    # get the comment text from the request
    comment = request.json.get('text')

    # Create a comment
    connection.execute(
        "INSERT INTO comments (owner, postid, text) "
        "VALUES (?, ?, ?)",
        (username, postid, comment)
    )

    # Get the comment id
    comment_id = connection.execute(
        "SELECT last_insert_rowid() AS comment_id"
    ).fetchone()

    comment_id = comment_id['comment_id']

    # Return the comment id
    context = {
        "comment_id": comment_id,
        "lognameOwnsThis": True,
        "owner": username,
        "ownerShowUrl": "/user/{username}/",
        "text": comment,
        "url": "/api/v1/comments/{comment_id}/"
    }
    return flask.jsonify(context), 201,
