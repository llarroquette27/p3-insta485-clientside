"""Sample docstring."""
import flask
from flask import session
import insta485


@insta485.app.route('/accounts/edit/')
def show_edit():
    """Display /accounts/edit/ route."""
    # Connect to database
    connection = insta485.model.get_db()

    if 'username' not in session:
        return flask.redirect('/accounts/login/')
    logname = session['username']

    # Query database
    cur = connection.execute(
        "SELECT username, fullname, email, filename AS owner_file "
        "FROM users "
        "WHERE username = ?",
        (logname,)
    )
    user = cur.fetchone()

    context = {"user": user, "logname": logname}
    return flask.render_template("edit.html", **context)
