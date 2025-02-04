"""Sample docstring."""
import flask
from flask import session
import insta485


@insta485.app.route('/users/<user_url_slug>/')
def show_user(user_url_slug):
    """Display /users/username route."""
    if 'username' not in session:
        return flask.redirect("/accounts/login/")

    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    logname = session['username']

    cur = connection.execute(
        "SELECT username, fullname, email, filename "
        "FROM users WHERE username = ?",
        (user_url_slug, )
    )
    user = cur.fetchone()
    if user is None:
        return flask.abort(404)

    cur = connection.execute(
        "SELECT postid, filename AS post_file FROM posts WHERE owner = ?",
        (user_url_slug, )
    )
    posts = cur.fetchall()

    cur = connection.execute(
        "SELECT COUNT(*) AS following_count "
        "FROM following WHERE username1 = ?",
        (user_url_slug, )
    )
    following_count = cur.fetchone()["following_count"]

    cur = connection.execute(
        "SELECT COUNT(*) AS follower_count "
        "FROM following WHERE username2 = ?",
        (user_url_slug,)
    )
    followers_count = cur.fetchone()["follower_count"]

    cur = connection.execute(
        "SELECT * FROM following WHERE username1 = ? AND username2 = ?",
        (logname, user_url_slug)
    )
    is_following = cur.fetchone() is not None

    context = {"user": user, "posts": posts,
               "following_count": following_count,
               "followers_count": followers_count,
               "is_following": is_following,
               "logname": logname}

    return flask.render_template("user.html", **context)
