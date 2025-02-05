"""Sample docstring."""
import flask
from flask import session, request
import insta485
import hashlib

# SHOULD WORK ONCE OTHER ROUTES IMPLEMENTED
@insta485.app.route('/api/v1/likes/<int:likeid>/', methods=['DELETE'])
def delete_like(likeid):
    """Sample docstring."""

    # User authentication
    connection = insta485.model.get_db()
    if 'username' not in session:
        if not flask.request.authorization:
            flask.abort(403)
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']

        real_password = connection.execute(
        "SELECT password FROM users "
        "WHERE username=? ",
        (username, )
        ).fetchone()

        real_password = real_password['password']
        if not real_password:
            flask.abort(403)

        salt = real_password.split('$')[1]

        algorithm = 'sha512'
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])

        if password_db_string != real_password:
            flask.abort(403)

        session['username'] = username

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
    