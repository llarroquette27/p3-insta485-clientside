"""Sample docstring."""
import flask
from flask import session
import insta485


@insta485.app.route('/accounts/password/')
def show_password():
    """Display /accounts/password/ route."""
    # Connect to database

    if 'username' not in session:
        return flask.redirect('/accounts/login/')
    logname = session['username']

    context = {"logname": logname}
    return flask.render_template("password.html", **context)
