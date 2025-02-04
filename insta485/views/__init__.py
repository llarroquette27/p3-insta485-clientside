"""Views, one for each Insta485 page."""
from insta485.views.index import show_index
from insta485.views.user import show_user
from insta485.views.post import show_post
from insta485.views.explore import show_explore
from insta485.views.edit import show_edit
from insta485.views.password import show_password
from insta485.views.follows import show_followers, show_following, post_follow
from insta485.views.accounts import show_create, show_delete, show_login
from insta485.views.accounts import show_logout, show_auth
from insta485.views.likes import post_likes
from insta485.views.comments import post_comment
from insta485.views.post_posts import post_post
