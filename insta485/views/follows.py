"""Sample docstring."""
import flask
from flask import session
import insta485


@insta485.app.route('/users/<username>/followers/')
def show_followers(username):
    """Sample docstring."""
    if 'username' not in session:
        return flask.redirect("/accounts/login/")

    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT * FROM users WHERE username=?",
        (username, )
    )
    user = cur.fetchone()
    if not user:
        flask.abort(404)

    cur = connection.execute(
        "SELECT * FROM following "
        "INNER JOIN users ON users.username=following.username1 "
        "WHERE username2 = ?",
        (username, )
    )
    followers = cur.fetchall()

    # Pre-process data to dictionary where key is
    # a follower and value is whether user follows back
    cur = connection.execute(
        "SELECT * FROM FOLLOWING WHERE username1=?",
        (username, )
    )
    following = cur.fetchall()
    # if not following:
    #     flask.abort(404)

    # Create set of all username is following
    following_set = set()
    for follow in following:
        following_set.add(follow['username2'])

    followers_dict = {}
    for follower in followers:
        if follower['username1'] in following_set:
            followers_dict[follower['username1']] = True
        else:
            followers_dict[follower['username1']] = False

    context = {"username": username, "followers": followers,
               "followers_dict": followers_dict}
    return flask.render_template("followers.html", **context)


@insta485.app.route('/users/<username>/following/')
def show_following(username):
    """Sample docstring."""
    if 'username' not in session:
        return flask.redirect("/accounts/login/")

    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT * FROM following "
        "INNER JOIN users ON users.username=following.username2 "
        "WHERE username1 = ?",
        (username, )
    )
    following = cur.fetchall()
    if not following:
        flask.abort(404)

    # Create set of all username is following
    following_set = set()
    for follow in following:
        following_set.add(follow['username2'])

    followers_dict = {}
    for follower in following:
        if follower['username2'] in following_set:
            followers_dict[follower['username2']] = True
        else:
            followers_dict[follower['username2']] = False

    context = {"username": username, "following": following,
               "followers_dict": followers_dict}
    return flask.render_template("following.html", **context)

# POST /following/?target=URL
# This endpoint only accepts POST requests.
# Follow or unfollow and immediately redirect to URL


LOGGER = flask.logging.create_logger(insta485.app)


@insta485.app.route('/following/', methods=['POST'])
def post_follow():
    """Sample docstring."""
    if 'username' not in session:
        return flask.redirect("/accounts/login/")

    logname = session['username']

    target = flask.request.args.get('target', '/')
    LOGGER.debug("target = %s", target)

    operation = flask.request.form["operation"]
    username = flask.request.form["username"]

    LOGGER.debug("username = %s", username)
    LOGGER.debug("operation = %s", operation)

    connection = insta485.model.get_db()

    if operation == "follow":
        # Error check
        cur = connection.execute(
            "SELECT * FROM following "
            "WHERE username1=? ",
            (logname, )
        )
        following = cur.fetchall()
        for follow in following:
            if follow['username2'] == username:
                flask.abort(409)

        # Post follow
        connection.execute(
            "INSERT INTO following (username1, username2) "
            "VALUES (?, ?) ",
            (logname, username)
        )
    else:
        # Error check
        cur = connection.execute(
            "SELECT * FROM following "
            "WHERE username1=? ",
            (logname, )
        )
        following = cur.fetchall()
        following_set = set()
        for follow in following:
            following_set.add(follow['username2'])

        if username not in following_set:
            flask.abort(409)

        # Post follow
        connection.execute(
            "DELETE FROM following "
            "WHERE username1=? AND username2=? ",
            (logname, username)
        )

    connection.commit()
    return flask.redirect(target)
