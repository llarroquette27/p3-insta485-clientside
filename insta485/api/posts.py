"""REST API for posts."""
import flask
from flask import session, request
import insta485
from .auth import authentication


@insta485.app.route('/api/v1/posts/')
def get_posts():
    """Sample docstring."""
    connection = insta485.model.get_db()

    authentication()

    username = session['username']

    # Get query strings used to filter
    limit = request.args.get('size', 10, type=int)  # Default is limit of 10
    postid_lte = request.args.get(
        'postid_lte', session.get('postid', None), type=int)

    if postid_lte is None:
        # Get the comment id
        post_id = connection.execute(
            "SELECT MAX(postid) FROM posts"
        ).fetchone()['MAX(postid)']
        postid_lte = post_id

    # Error check the query strings
    if limit < 0 or request.args.get('page', 0, type=int) < 0:
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
        (username, username, username, postid_lte, limit,
            (limit * request.args.get('page', 0, type=int)))
    ).fetchall()

    # If not postid_lte, get current newest post
    # newest_post = 0
    if postid_lte is None:
        for post in posts:
            newest_post = max(newest_post, post['postid'])
        postid_lte = newest_post

    # session['postid'] = newest_post

    # Compute next string
    if len(posts) < limit:
        next_url = ""
    else:
        next_url = f"/api/v1/posts/?size={limit}"
        next_url += f"&page={request.args.get('page', 0, type=int) + 1}"
        next_url += f"&postid_lte={postid_lte}"

    results = [
        {
            "postid": post["postid"],
            "url": f"/api/v1/posts/{post['postid']}/"
        }
        for post in posts
    ]

    if request.query_string.decode('utf-8'):
        response = {
            "next": next_url,
            "results": results,
            "url": f"{request.path}?{request.query_string.decode('utf-8')}"
        }
    else:
        response = {
            "next": next_url,
            "results": results,
            "url": f"{request.path}"
        }

    return flask.jsonify(response)
