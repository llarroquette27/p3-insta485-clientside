"""REST API for posts."""
import flask
from flask import session, request
import insta485
import hashlib


@insta485.app.route('/api/v1/posts/')
def get_posts():
    """Sample docstring."""
    if 'username' in session:
        print(session['username'])
    if 'postid' in session:
        print(session['postid'])

    connection = insta485.model.get_db()

    # User authentication
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

    # Get query strings used to filter
    limit = request.args.get('size', 10, type=int)  # Default is limit of 10
    postid_lte = request.args.get(
        'postid_lte', session.get('postid', None), type=int)
    page = request.args.get('page', 0, type=int)

    if postid_lte is None:
        # Get the comment id
        post_id = connection.execute(
            "SELECT MAX(postid) FROM posts"
        ).fetchone()['MAX(postid)']
        postid_lte = post_id

    # Error check the query strings
    if limit < 0 or page < 0:
        flask.abort(400)

    # Query gets all possible posts, later we will filter
    posts = connection.execute(
        "SELECT DISTINCT posts.postid, posts.owner, posts.created, "
        "users.filename AS owner_file, posts.filename AS post_file "
        "FROM posts "
        "INNER JOIN users ON users.username=posts.owner "
        "LEFT JOIN following ON posts.owner=following.username2 "
        "AND following.username1 = ? "
        "WHERE following.username1 = ? OR "
        "posts.owner = ? AND posts.postid <= ? "
        "ORDER BY posts.postid DESC "
        "LIMIT ? OFFSET ?",
        (username, username, username, postid_lte, limit, (limit * page))
    ).fetchall()

    # If not postid_lte, get current newest post
    newest_post = 0
    if postid_lte is None:
        for post in posts:
            newest_post = max(newest_post, post['postid'])
        postid_lte = newest_post

    # session['postid'] = newest_post

    # Compute next string
    if len(posts) < limit:
        next = ""
    else:
        next = f"/api/v1/posts/?size={limit}&page={page + 1}"
        next += f"&postid_lte={postid_lte}"

    results = [
        {
            "postid": post["postid"],
            "url": f"/api/v1/posts/{post['postid']}/"
        }
        for post in posts
    ]

    path = request.path
    query_string = request.query_string.decode('utf-8')

    if query_string:
        response = {
            "next": next,
            "results": results,
            "url": f"{path}?{query_string}"
        }
    else:
        response = {"next": next, "results": results, "url": f"{path}"}

    return flask.jsonify(response)
