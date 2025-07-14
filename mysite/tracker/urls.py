from django.urls import path, include, re_path
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
    path('auth/signup/', signup_view, name='signup'),

    # web google log-in

    path('dj-rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),

    # API endpoints
    path('categories/', CategoryList.as_view(), name='category-list'),
    path('categories/<int:category_id>/tracks/', LearningTracksByCategory.as_view(), name='tracks-by-category'),
    path('tracks/<int:trackId>/', LearningTrackDetail.as_view(), name='user-track-retrieve'),

    path('user/tracks/', UserLearningTrackList.as_view(), name='user-learning-tracks-list'),
    path('user/tracks/<int:learning_track_id>/<int:user_learning_track_id>/', UserLearningTrackDetail.as_view(),
         name='user-learning-track'),
    path('user/tracks/<int:user_learning_track_id>/generate-task/', GenerateNextTask.as_view(),
         name='generate-next-task'),
    path('user/tasks/<int:pk>/', TaskDetail.as_view(), name='task-detail'),

    # Test endpoints
    path('test-auth/', TestAuthView.as_view(), name='test-auth'),

]
