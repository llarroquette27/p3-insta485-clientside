"""Sample docstring."""
import flask
from flask import session
import arrow
import insta485


@insta485.app.route('/posts/<postid_url_slug>/')
def show_post(postid_url_slug):
    """Display /posts/postid route."""
    if 'username' not in session:
        return flask.redirect("/accounts/login/")
    username = session['username']

    # Connect to database
    connection = insta485.model.get_db()

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
        (postid_url_slug, "awdeorio", )
    ).fetchone() is not None

    post['created'] = arrow.get(post['created']).humanize()

    context = {"post": post, "owner": owner,
               "comments": comments, "likes": likes, "logname": username,
               "liked": liked}
    return flask.render_template("post.html", **context)
