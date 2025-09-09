from django.urls import path, re_path
from django.http import HttpResponseNotFound
from .views import *

app_name = "tracker"

accounts_blocker = re_path(
    r'^accounts/(?!google/login|google/login/callback).*$',  # allow only Google login
    lambda request: HttpResponseNotFound()  # or: redirect_to_frontend
)

urlpatterns = [

    # web general log-in
    path('auth/csrf/', set_csrf_cookie, name='csrf'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/signup/', signup_view, name='signup'),
    path('upgrade-to-pro/', upgrade_to_pro, name='upgrade-to-pro'),

    # web google log-in
    path('dj-rest-auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('dj-rest-auth/user/', CustomUserDetailsView.as_view(), name='rest_user_details'),
    path('dj-rest-auth/password/reset/', CustomPasswordResetView.as_view(), name='password_reset'),

    # API endpoints
    path('categories/', CategoryList.as_view(), name='category-list'),
    path('categories/<int:category_id>/tracks/', LearningTracksByCategory.as_view(), name='tracks-by-category'),
    path('tracks/<int:trackId>/', LearningTrackDetail.as_view(), name='user-track-retrieve'),

    path('custom-track/create/', CustomTrackCreateView.as_view(), name='custom-track-create'),
    path('custom-track/options/', CustomTrackOptionsView.as_view(), name='custom-track-options'),

    path('user/tracks/', UserLearningTrackList.as_view(), name='user-learning-tracks-list'),
    path('user/tracks/<int:learning_track_id>/<int:user_learning_track_id>/', UserLearningTrackDetail.as_view(),
         name='user-learning-track'),
    path('user/tracks/<int:user_learning_track_id>/generate-task/', GenerateNextTask.as_view(),
         name='generate-next-task'),
    path('user/tasks/<int:pk>/', TaskDetail.as_view(), name='task-detail'),

]
