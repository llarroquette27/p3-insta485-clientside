"""REST API for posts."""
import flask
from flask import session, request
import insta485
import hashlib

@insta485.app.route('/api/v1/posts/')
def show_posts():
  connection = insta485.model.get_db()

  # User authentication
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
    
  # Get query strings
  limit = request.args.get('size', 10, type=int) # Default is limit of 10
  postid = request.args.get('postid_lte', session.get('postid', None), type=int)
  page = request.args.get('page', 1, type=int) 

  # Add error checking 
  if limit < 0 or page < 0:
    flask.abort(400)
  
  
  # Update query to include query strings
  posts = connection.execute(
    "SELECT DISTINCT posts.postid, posts.owner, posts.created, "
    "users.filename AS owner_file, posts.filename AS post_file "
    "FROM posts "
    "INNER JOIN users ON users.username=posts.owner "
    "LEFT JOIN following ON posts.owner=following.username2 "
    "AND following.username1 = ? "
    "WHERE following.username1 = ? OR posts.owner = ? "
    "ORDER BY posts.postid DESC " 
    "LIMIT ? ",
    (username, username, username, limit,)
  ).fetchall()
  print(posts)

  # Store most recent post id in session - loop through posts, find highest id
  most_recent = 0
  for post in posts:
    if post['postid'] > most_recent:
      most_recent = max(post['postid'], most_recent)
  session['postid'] = most_recent
  final_postid = most_recent

  # Computer next string
  if len(posts) < limit:
    next = ""
  else:
    next = f"/api/v1/posts/?size={limit}&page={page}&postid_lte={final_postid}"

  results = [{"postid": post["postid"], "url": f"/api/v1/posts/{post['postid']}/"} for post in posts]

  response = {"next": next, "results": results, "url": "/api/v1/posts/"}
  print(response)

  return flask.jsonify(response)

  
@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
  """Return post on postid.

  Example:
  {
    "created": "2017-09-28 04:33:28",
    "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
    "owner": "awdeorio",
    "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
    "ownerShowUrl": "/users/awdeorio/",
    "postShowUrl": "/posts/1/",
    "postid": 1,
    "url": "/api/v1/posts/1/"
  }
  """
  context = {
      "created": "2017-09-28 04:33:28",
      "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
      "owner": "awdeorio",
      "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
      "ownerShowUrl": "/users/awdeorio/",
      "postShowUrl": f"/posts/{postid_url_slug}/",
      "postid": postid_url_slug,
      "url": flask.request.path,
  }
  return flask.jsonify(**context)
