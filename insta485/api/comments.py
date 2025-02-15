"""Add one comment to a post."""
import flask
from flask import session, request
import insta485
from .auth import authentication


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def post_comments():
    """Sample docstring."""
    # User authentication
    connection = insta485.model.get_db()
    authentication()

    username = session['username']

    postid = request.args.get('postid')
    # get the comment text from the request
    comment = request.json.get('text')

    # Create a comment
    connection.execute(
        "INSERT INTO comments (owner, postid, text) "
        "VALUES (?, ?, ?)",
        (username, postid, comment)
    )

    # Get the comment id
    comment_id = connection.execute(
        "SELECT last_insert_rowid() AS comment_id"
    ).fetchone()

    comment_id = comment_id['comment_id']

    # Return the comment id
    context = {
        "comment_id": comment_id,
        "lognameOwnsThis": True,
        "owner": username,
        "ownerShowUrl": "/user/{username}/",
        "text": comment,
        "url": "/api/v1/comments/{comment_id}/"
    }
    return flask.jsonify(context), 201
