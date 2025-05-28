from django.urls import path
from .views import *

app_name = "tracker"

urlpatterns = [

    path('categories/', CategoryList.as_view(), name='category-list'),

    path('categories/<int:category_id>/tracks/', LearningTracksByCategory.as_view(), name='tracks-by-category'),

    path('user/tracks/', UserLearningTrackList.as_view(), name='user-learning-tracks-list'),
    path('user/tracks/manage/', UserLearningTrackCreateDelete.as_view(), name='user-learning-tracks-manage'),
    path('user/tracks/<int:pk>/', LearningTrackDetail.as_view(), name='learning-track-detail'),

    path('user/tasks/<int:pk>/', TaskDetail.as_view(), name='task-detail'),

    path('user/notes/<int:pk>/', NoteDetail.as_view(), name='note-detail'),

    path('user/tracks/<int:track_id>/generate-task/', GenerateNextTask.as_view(), name='generate-next-task'),
    path('test-auth/', TestAuthView.as_view(), name='test-auth'),
]