"""REST API for posts."""
import flask
from flask import session, request
import insta485
import hashlib

@insta485.app.route('/api/v1/posts/')
def get_posts():
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
  
  # Query gets all possible posts, later we will filter
  posts = connection.execute(
    "SELECT DISTINCT posts.postid, posts.owner, posts.created, "
    "users.filename AS owner_file, posts.filename AS post_file "
    "FROM posts "
    "INNER JOIN users ON users.username=posts.owner "
    "LEFT JOIN following ON posts.owner=following.username2 "
    "AND following.username1 = ? "
    "WHERE following.username1 = ? OR posts.owner = ? "
    "ORDER BY posts.postid DESC ",
    (username, username, username,)
  ).fetchall()

  # Get query strings used to filter
  limit = request.args.get('size', 10, type=int) # Default is limit of 10
  postid = request.args.get('postid_lte', session.get('postid', None), type=int)
  page = request.args.get('page', 1, type=int) 

  # Error check the query strings
  if limit < 0 or page < 0:
    flask.abort(400)

  # Filter by postid_lte and by last session
  # Filers by postid_lte if it exists
  filtered_posts = []
  if postid:
    for post in posts:
      if post['postid'] <= postid:
        filtered_posts.append(post)
    posts = filtered_posts
  
  # Filters by oldest post from last request from session
  filtered_posts = []
  if 'last_post' in session:
    for post in posts:
      if post['postid'] < session['last_post']:
        filtered_posts.append(post)
    posts = filtered_posts

  # Filters limit (or 10) most recent posts
  filtered_posts = sorted(posts, key=lambda x: x['postid'], reverse=True)[:limit]
  posts = filtered_posts

  # TO-DO: PAGES?
  # NOT SURE WHAT PAGES ARE FOR

  # Gets oldest post to save for next query for filtering
  oldest_post = float('inf')
  for post in posts:
    oldest_post = min(post['postid'], oldest_post)
  
  session['last_post'] = oldest_post # Remembers last post for next query

  # If not postid_lte, get current newest post -> this is for the next request
  newest_post = 0
  if postid is None:
    for post in posts:
      newest_post = max(newest_post, post['postid'])
    postid = newest_post

  # Compute next string
  if len(posts) < limit:
    next = ""
  else:
    next = f"/api/v1/posts/?size={limit}&page={page}&postid_lte={postid}"

  results = [{"postid": post["postid"], "url": f"/api/v1/posts/{post['postid']}/"} for post in posts]

  path = request.path
  query_string = request.query_string.decode('utf-8')

  if query_string:
    response = {"next": next, "results": results, "url": f"{path}?{query_string}"}
  else:
    response = {"next": next, "results": results, "url": f"{path}"}
  print(request)

  return flask.jsonify(response)
