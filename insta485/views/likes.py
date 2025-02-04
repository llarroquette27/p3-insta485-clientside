"""Sample docstring."""
import flask
import insta485

# POST /likes/?target=URL
# This endpoint only accepts POST requests.
# Create or delete a like and immediately redirect to URL


LOGGER = flask.logging.create_logger(insta485.app)


@insta485.app.route('/likes/', methods=['POST'])
def post_likes():
    """Sample docstring."""
    LOGGER.debug("operation = %s", flask.request.form["operation"])
    LOGGER.debug("postid = %s", flask.request.form["postid"])

    operation = flask.request.form["operation"]

    target = flask.request.args.get('target', '/')
    LOGGER.debug("target = %s", target)

    logname = "awdeorio"

    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT COUNT(*) AS count "
        "FROM likes "
        "WHERE owner = ? AND postid = ?",
        (logname, flask.request.form["postid"])
    )
    count = cur.fetchone()['count']

    if count == 0:
        if flask.request.form["operation"] == "unlike":
            flask.abort(409)
        # Create a like

        # Error check
        if operation == "unlike":
            flask.abort(409)

        connection.execute(
            "INSERT INTO likes (owner, postid) "
            "VALUES (?, ?)",
            (logname, flask.request.form["postid"])
        )
    else:
        # Delete a like

        # Error check
        if operation == "like":
            flask.abort(409)

        connection.execute(
            "DELETE FROM likes "
            "WHERE owner = ? AND postid = ?",
            (logname, flask.request.form["postid"])
        )

    connection.commit()

    return flask.redirect(target)
