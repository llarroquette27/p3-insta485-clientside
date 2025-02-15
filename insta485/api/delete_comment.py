"""Delete a comment."""
import flask
from flask import session, request
import insta485
from .auth import authentication


@insta485.app.route('/api/v1/comments/<int:commentid>/', methods=['DELETE'])
def delete_comment(commentid):
    """Delete a comment."""
    # User authentication
    connection = insta485.model.get_db()
    authentication()

    username = session['username']

    # Check if the comment exists
    comment = connection.execute(
        "SELECT * FROM comments "
        "WHERE commentid=?",
        (commentid, )
    ).fetchone()

    if not comment:
        flask.abort(404)

    # Check if the user owns the comment
    if comment['owner'] != username:
        flask.abort(403)

    # Delete the comment
    connection.execute(
        "DELETE FROM comments "
        "WHERE commentid=?",
        (commentid, )
    )

    connection.commit()

    return (request.url + str(commentid) + "/"), 204
