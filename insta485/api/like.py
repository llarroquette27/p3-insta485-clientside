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

    postid = request.args.get('postid')
    print(username)
    print(postid)

    cur = connection.execute(
        "SELECT COUNT(*) AS count "
        "FROM likes "
        "WHERE owner = ? AND postid = ?",
        (username, postid)
    )
    count = cur.fetchone()['count']
    print(count)

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
        (username, flask.request.form["postid"])
       ).fetchone()['likeid']
       return flask.jsonify({"likeid": likeid, "url": request.path})

    connection.commit()

    likeid = connection.execute(
        "SELECT last_insert_rowid() FROM posts"
    ).fetchone()
    response = {"likeid": likeid, "url": request.path}

    return flask.jsonify(response), 201
