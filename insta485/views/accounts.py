"""Sample docstring."""
import flask
from flask import session
import insta485

from insta485.views.accounts_login import login_account
from insta485.views.accounts_create import create_account
from insta485.views.accounts_delete import delete_account
from insta485.views.accounts_edit import edit_account
from insta485.views.update_password import update_password

LOGGER = flask.logging.create_logger(insta485.app)


@insta485.app.route('/accounts/login/')
def show_login():
    """Sample docstring."""
    if 'username' in session:
        return flask.redirect("/")
    return flask.render_template("accountsLogin.html")


@insta485.app.route('/accounts/create/')
def show_create():
    """Sample docstring."""
    if 'username' in session:
        return flask.redirect("/accounts/edit/")
    return flask.render_template("accountsCreate.html")


@insta485.app.route('/accounts/delete/')
def show_delete():
    """Sample docstring."""
    logname = session["username"]
    context = {"logname": logname}
    return flask.render_template("accountsDelete.html", **context)


@insta485.app.route('/accounts/logout/', methods=['POST'])
def show_logout():
    """Sample docstring."""
    # only accept POST requests
    # immediately redirect to /accounts/login/
    # log out the user
    flask.session.clear()
    return flask.redirect("/accounts/login/")


@insta485.app.route('/accounts/auth/')
def show_auth():
    """Sample docstring."""
    # Quick rundown of what it does and what it's missing:
    # Checks if the user is already logged in
    # If they are, return a 200 status code
    # If they're not, return a 403 status code
    # Missing: actually checking if the user is logged in -
    # just uses the 'logname' key in the session
    if 'username' in flask.session:
        return flask.Response(status=200)
    flask.abort(403)


@insta485.app.route('/accounts/', methods=['POST'])
def post_account():
    """Sample docstring."""
    target = flask.request.args.get('target', "/")
    LOGGER.debug("target = %s", target)

    operation = flask.request.form["operation"]

    if operation == "login":
        # Login
        username = flask.request.form["username"]
        password = flask.request.form["password"]

        login_account(username, password)
    elif operation == "create":
        # Create
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        fullname = flask.request.form["fullname"]
        email = flask.request.form["email"]
        user_file = flask.request.files["file"]

        create_account(username, password, fullname, email, user_file)
    elif operation == "delete":
        delete_account()
    elif operation == "edit_account":
        fullname = flask.request.form["fullname"]
        email = flask.request.form["email"]
        user_file = flask.request.files["file"]

        edit_account(fullname, email, user_file)
    else:
        password = flask.request.form["password"]
        new_password1 = flask.request.form["new_password1"]
        new_password2 = flask.request.form["new_password2"]

        update_password(password, new_password1, new_password2)

    # return flask.redirect(target)
    return flask.redirect(target)
