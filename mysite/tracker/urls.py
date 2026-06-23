from django.urls import path, re_path
from django.http import HttpResponseNotFound

from .views.auth_views import (
    set_csrf_cookie, login_view, logout_view,
    signup_view, upgrade_to_pro, GoogleLoginView,
    CustomUserDetailsView, CustomPasswordResetView,
)
from .views.learning_views import (
    CategoryList, LearningTracksByCategory,
    LearningTrackDetail, UserLearningTrackList, UserLearningTrackDetail,
    GenerateSummary,
)
from .views.ai_views import (
    CustomTrackOptionsView, CustomTrackCreateView,
    TaskDetail, GenerateNextTask, RestartTrack,
)

app_name = "tracker"

accounts_blocker = re_path(
    r'^accounts/(?!google/login|google/login/callback).*$',
    lambda request: HttpResponseNotFound()
)

urlpatterns = [

    # Auth
    path('auth/csrf/',           set_csrf_cookie,                  name='csrf'),
    path('auth/login/',          login_view,                       name='login'),
    path('auth/logout/',         logout_view,                      name='logout'),
    path('auth/signup/',         signup_view,                      name='signup'),
    path('auth/google/',         GoogleLoginView.as_view(),        name='google-login'),
    path('auth/user/',           CustomUserDetailsView.as_view(),  name='user-details'),
    path('auth/password/reset/', CustomPasswordResetView.as_view(), name='password-reset'),

    # User
    path('user/upgrade-to-pro/', upgrade_to_pro, name='upgrade-to-pro'),

    # Catalog
    path('categories/',                          CategoryList.as_view(),             name='category-list'),
    path('categories/<int:category_id>/tracks/', LearningTracksByCategory.as_view(), name='tracks-by-category'),
    path('tracks/<int:trackId>/',                LearningTrackDetail.as_view(),      name='track-detail'),

    # User Tracks
    path('user/tracks/',
         UserLearningTrackList.as_view(),
         name='user-track-list'),

    path('user/tracks/<int:user_learning_track_id>/',
         UserLearningTrackDetail.as_view(),
         name='user-track-detail'),

    path('user/tracks/<int:user_learning_track_id>/generate-task/',
         GenerateNextTask.as_view(),
         name='generate-next-task'),

    path('user/tracks/<int:user_learning_track_id>/summary/',
         GenerateSummary.as_view(),
         name='generate-summary'),

    path('user/tracks/<int:user_learning_track_id>/restart/',
         RestartTrack.as_view(),
         name='restart-track'),

    # Tasks
    path('user/tasks/<int:pk>/',
         TaskDetail.as_view(),
         name='task-detail'),

    # Custom Tracks (Pro)
    path('custom-track/options/', CustomTrackOptionsView.as_view(), name='custom-track-options'),
    path('custom-track/create/',  CustomTrackCreateView.as_view(),  name='custom-track-create'),
]