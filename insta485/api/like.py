"""Sample docstring."""
import flask
from flask import session, request
import insta485
import hashlib


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def post_api_likes():
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

    # Get post data
    highest_post_id = connection.execute(
        "SELECT MAX(postid) AS max_postid FROM posts"
    ).fetchone()

    highest_post_id = highest_post_id['max_postid']

    postid = request.args.get('postid')

    if int(postid) > highest_post_id or highest_post_id < 1:
        flask.abort(404)

    cur = connection.execute(
        "SELECT COUNT(*) AS count "
        "FROM likes "
        "WHERE owner = ? AND postid = ?",
        (username, postid)
    )
    count = cur.fetchone()['count']

    if count == 0:
        # Create a like
        connection.execute(
            "INSERT INTO likes (owner, postid) "
            "VALUES (?, ?)",
            (username, postid)
        )
    else:
        # Like already exists, return 200 ok
        likeid = connection.execute(
            "SELECT likeid FROM likes "
            "WHERE owner = ? AND postid = ?",
            (username, postid)
        ).fetchone()['likeid']
        return flask.jsonify({"likeid": likeid, "url": request.path + str(likeid) +"/"})

    connection.commit()

    likeid = connection.execute(
        "SELECT last_insert_rowid() FROM posts"
    ).fetchone()
    response = {"likeid": likeid, "url": request.path + str(likeid) +"/"}

    return flask.jsonify(response), 201