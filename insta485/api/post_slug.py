"""REST API for posts."""
import flask
from flask import session
import insta485
from .auth import authentication


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Sample docstring."""
    connection = insta485.model.get_db()

    authentication()

    # Get post data
    highest_post_id = connection.execute(
        "SELECT MAX(postid) AS max_postid FROM posts"
    ).fetchone()

    highest_post_id = highest_post_id['max_postid']

    if postid_url_slug > highest_post_id or highest_post_id < 1:
        flask.abort(404)

    # Query database
    post = connection.execute(
        "SELECT postid, owner, filename AS post_file, created "
        "FROM posts WHERE postid = ?",
        (postid_url_slug, )
    ).fetchall()[0]

    if post is None:
        return flask.abort(404)

    owner = connection.execute(
        "SELECT username, filename AS owner_file "
        "FROM users WHERE username = ?",
        (post['owner'], )
    ).fetchone()

    comments = connection.execute(
        "SELECT owner, text, commentid "
        "FROM comments WHERE postid = ?",
        (postid_url_slug, )
    ).fetchall()

    likes = connection.execute(
        "SELECT COUNT(*) "
        "FROM likes WHERE postid = ?",
        (postid_url_slug, )
    ).fetchone()["COUNT(*)"]

    liked = connection.execute(
        "SELECT * "
        "FROM likes WHERE postid = ? AND owner = ?",
        (postid_url_slug, session['username'], )
    ).fetchone() is not None

    liked_url = None

    if liked:
        likeid = connection.execute(
            "SELECT likeid "
            "FROM likes WHERE postid = ? AND owner = ?",
            (postid_url_slug, session['username'], )
        ).fetchone()
        liked_url = "/api/v1/likes/" + str(likeid["likeid"]) + "/"

    comments = [
        {
            "commentid": comment["commentid"],
            "lognameOwnsThis": comment["owner"] == session['username'],
            "owner": comment["owner"],
            "ownerShowUrl": "/users/" + comment["owner"] + "/",
            "text": comment["text"],
            "url": "/api/v1/comments/" + str(comment["commentid"]) + "/"
        }
        for comment in comments]

    return flask.jsonify({
        "comments": comments,
        "comments_url": "/api/v1/comments/?postid=" + str
        (postid_url_slug),
        "created": post["created"],
        "imgUrl": "/uploads/" + post["post_file"],
        "likes": {
            "lognameLikesThis": liked,
            "numLikes": likes,
            "url": liked_url
        },
        "owner": owner["username"],
        "ownerImgUrl": "/uploads/" + owner["owner_file"],
        "ownerShowUrl": "/users/" + owner["username"] + "/",
        "postShowUrl": "/posts/" + str(postid_url_slug) + "/",
        "postid": postid_url_slug,
        "url": "/api/v1/posts/" + str(postid_url_slug) + "/"
    })
