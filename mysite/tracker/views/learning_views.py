from django.shortcuts import get_object_or_404

from rest_framework import mixins, status
from rest_framework.generics import RetrieveAPIView, ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Category, LearningTrack, UserLearningTrack
from ..serializers import (
    CategorySerializer,
    LearningTrackListSerializer,
    LearningTrackDetailSerializer,
    UserLearningTrackSerializer,
)
from ..services.track_service import generate_and_save_summary


class CategoryList(ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Category.objects.all()
        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(language=language)
        return queryset


class LearningTracksByCategory(ListAPIView):
    serializer_class = LearningTrackListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return LearningTrack.objects.filter(category_id=self.kwargs['category_id'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class LearningTrackDetail(RetrieveAPIView):
    queryset = LearningTrack.objects.all()
    serializer_class = LearningTrackDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "trackId"

    def get_object(self):
        return get_object_or_404(LearningTrack, pk=self.kwargs.get("trackId"))


class UserLearningTrackList(mixins.ListModelMixin, mixins.CreateModelMixin, GenericAPIView):
    serializer_class = UserLearningTrackSerializer

    def get_queryset(self):
        return UserLearningTrack.objects.filter(user=self.request.user).select_related(
            'learning_track'
        ).prefetch_related(
            'learning_track__category'
        )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        learning_track = get_object_or_404(LearningTrack, pk=request.data.get("learning_track"))
        ult, created = UserLearningTrack.objects.get_or_create(
            user=request.user, learning_track=learning_track
        )
        serializer = self.get_serializer(ult)
        return Response(serializer.data, status=201 if created else 200)

    def delete(self, request, *args, **kwargs):
        ult_id = (
            request.data.get("user_learning_track_id")
            or request.query_params.get("user_learning_track_id")
        )
        if not ult_id:
            return Response(
                {"error": "user_learning_track_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        user_track = get_object_or_404(UserLearningTrack, pk=ult_id, user=request.user)
        user_track.delete()
        return Response({"detail": "Track deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class UserLearningTrackDetail(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                               mixins.RetrieveModelMixin, GenericAPIView):
    serializer_class = UserLearningTrackSerializer

    def get_queryset(self):
        return UserLearningTrack.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(
            UserLearningTrack,
            pk=kwargs.get('user_learning_track_id'),
            user=request.user,
        )
        return Response(self.get_serializer(obj).data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GenerateSummary(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_learning_track_id):
        user_track = get_object_or_404(
            UserLearningTrack,
            pk=user_learning_track_id,
            user=request.user
        )
        summary = generate_and_save_summary(user_track)
        if summary is None:
            return Response(
                {"error": "Failed to generate summary."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response({"summary": summary})