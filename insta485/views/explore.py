"""Sample docstring."""
import flask
from flask import session
import insta485


@insta485.app.route('/explore/')
def show_explore():
    """Display /explore/ route."""
    if 'username' not in session:
        return flask.redirect('/accounts/login/')
    logname = session['username']

    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    cur = connection.execute(
        "SELECT username, filename AS owner_file "
        "FROM users "
        "WHERE username NOT IN ( "
        "    SELECT username2 "
        "    FROM following "
        "    WHERE username1 = ? "
        ") AND username != ?",
        (logname, logname)
    )
    users = cur.fetchall()

    context = {"users": users, "logname": logname}
    return flask.render_template("explore.html", **context)
