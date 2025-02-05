"""REST API for posts."""
import flask
from flask import session, request
import insta485
import hashlib


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    connection = insta485.model.get_db()

    # User authentication
    if 'username' not in session:
        print("No username in session")
        if not request.authorization:
            flask.abort(403)
        username = request.authorization['username']
        password = request.authorization['password']

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

    if postid_url_slug > highest_post_id or highest_post_id < 1:
        flask.abort(404)

    # Query database
    post = connection.execute(
        "SELECT postid, owner, filename AS post_file, created "
        "FROM posts WHERE postid = ?",
        (postid_url_slug, )
    ).fetchone()
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
        (postid_url_slug, username, )
    ).fetchone() is not None

    if liked:
        likeid = connection.execute(
            "SELECT likeid "
            "FROM likes WHERE postid = ? AND owner = ?",
            (postid_url_slug, username, )
        ).fetchone()
        liked_url = "/api/v1/likes/" + str(likeid["likeid"]) + "/"

    comments = [
        {
            "commentid": comment["commentid"],
            "lognameOwnsThis": comment["owner"] == username,
            "owner": comment["owner"],
            "ownerShowUrl": "/users/" + comment["owner"] + "/",
            "text": comment["text"],
            "url": "/api/v1/comments/" + str(comment["commentid"]) + "/"
        }
        for comment in comments]

    likes_json = {
            "lognameLikesThis": liked,
            "numLikes": likes,
            "url": liked_url
    }

    context = {
        "comments": comments,
        "comments_url": "/api/v1/comments/?postid=" + str
        (postid_url_slug),
        "created": post["created"],
        "imgUrl": "/uploads/" + post["post_file"],
        "likes": likes_json, "owner": owner["username"],
        "ownerImgUrl": "/uploads/" + owner["owner_file"],
        "ownerShowUrl": "/users/" + owner["username"] + "/",
        "postShowUrl": "/posts/" + str(postid_url_slug) + "/",
        "postid": postid_url_slug,
        "url": "/api/v1/posts/" + str(postid_url_slug) + "/"
    }

    return flask.jsonify(context)
