"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import arrow
from flask import send_from_directory, session
import insta485


@insta485.app.route('/uploads/<filename>')
def download_file(filename):
    """Download a file."""
    if 'username' not in session:
        flask.abort(403)

    connection = insta485.model.get_db()

    file = connection.execute(
            "SELECT * FROM users "
            "WHERE filename=? ",
            (filename, )
    ).fetchone()
    if not file:
        file = connection.execute(
            "SELECT * FROM posts "
            "WHERE filename=? ",
            (filename, )
        ).fetchone()
        if not file:
            flask.abort(404)

    return send_from_directory(insta485.app.config['UPLOAD_FOLDER'], filename,
                               as_attachment=True)


@insta485.app.route('/')
def show_index():
    """Display / route."""
    if 'username' not in session:
        return flask.redirect('/accounts/login/')

    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    logname = session['username']

    user = connection.execute(
        "SELECT * "
        "FROM users "
        "WHERE username = ?",
        (logname,)
    ).fetchone()
    if not user:
        session.pop('username', None)
        return flask.redirect('/accounts/login/')

    posts = connection.execute(
        "SELECT DISTINCT posts.postid, posts.owner, posts.created, "
        "users.filename AS owner_file, posts.filename AS post_file "
        "FROM posts "
        "INNER JOIN users ON users.username=posts.owner "
        "LEFT JOIN following ON posts.owner=following.username2 "
        "AND following.username1 = ? "
        "WHERE following.username1 = ? OR posts.owner = ? "
        "ORDER BY posts.postid DESC",
        (logname, logname, logname, )
    ).fetchall()
    comments = connection.execute(
        "SELECT * "
        "FROM comments"
    ).fetchall()
    likes = connection.execute(
        "SELECT * "
        "FROM likes"
    ).fetchall()

    # For each post, see if user (awedorio) liked it
    liked_post_dict = {}
    for post in posts:
        liked_post_dict[post['postid']] = False

    for like in likes:
        if like['owner'] == logname:
            liked_post_dict[like['postid']] = True

    # CONVERT TO HUMANIZED TIME USING ARROW HERE
    for post in posts:
        post['created'] = arrow.get(post['created']).humanize()

    # Add database info to context
    context = {"posts": posts, "comments": comments, "likes": likes,
               "liked_post_dict": liked_post_dict, "logname": logname}
    return flask.render_template("index.html", **context)
