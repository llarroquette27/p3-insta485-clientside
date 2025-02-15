"""Sample docstring."""
import flask
from flask import session, request
import insta485
from .auth import authentication


@insta485.app.route('/api/v1/likes/<int:likeid>/', methods=['DELETE'])
def delete_like(likeid):
    """Sample docstring."""
    # User authentication
    connection = insta485.model.get_db()
    authentication()

    username = session['username']
    # likeid = request.args.get('likeid')

    # Check to make sure like exists
    like = connection.execute(
        "SELECT * FROM likes "
        "WHERE likeid=?",
        (likeid,)
    ).fetchone()
    if not like:
        flask.abort(404)

    # Check that user owns like
    if like['owner'] != username:
        flask.abort(403)

    connection.execute(
        "DELETE FROM likes "
        "WHERE likeid=?",
        (likeid,)
    )

    connection.commit()

    return (request.url + str(likeid) + "/"), 204
