"""Sample docstring."""
import flask
from flask import session
import insta485

LOGGER = flask.logging.create_logger(insta485.app)


@insta485.app.route('/comments/', methods=['POST'])
def post_comment():
    """Comments docstring."""
    if 'username' not in session:
        return flask.redirect('/accounts/login/')
    logname = session['username']

    target = flask.request.args.get('target', '/')
    LOGGER.debug("target = %s", target)

    operation = flask.request.form["operation"]

    connection = insta485.model.get_db()

    if operation == "create":
        postid = flask.request.form['postid']
        text = flask.request.form['text']

        # Error check
        if text == "":
            flask.abort(400)

        connection.execute(
            "INSERT INTO comments (owner, postid, text) "
            "VALUES (?, ?, ?) ",
            (logname, postid, text, )
        )
    else:
        commentid = flask.request.form["commentid"]

        # Error Check
        cur = connection.execute(
            "SELECT * FROM comments "
            "WHERE commentid=? ",
            (commentid, )
        )
        comment = cur.fetchone()
        print("Comment:", commentid)
        if comment['owner'] != logname:
            flask.abort(403)

        # Delete
        connection.execute(
            "DELETE FROM comments "
            "WHERE commentid=?",
            (commentid, )
        )

    connection.commit()
    return flask.redirect(target)
