from django.contrib.auth.models import User
from guardian.shortcuts import assign_perm
from permissions.services import APIPermissionClassFactory
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from story.models import Story
from story.serializers import StorySerializer
from viewedStory.models import ViewedStory
from viewedStory.serializers import ViewedStorySerializer


def evaluate(user, obj, request):
    return user.id == obj.user.id

class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = (
        APIPermissionClassFactory(
            name='EventPermission',
            permission_configuration={
                'base': {
                    'create': True,
                    'list': True,
                },
                'instance': {
                    'destroy': evaluate,
                    'partial_update': False,
                    'retrieve': True,
                    'update': False,
                    'views': evaluate
                }
            }
        ),
    )

    @action(detail=True, methods=['get'])
    def views(self, request, pk=None):
        story = self.get_object()
        response = []
        for view in ViewedStorySerializer.objects.filter(story=story):
            response.append(ViewedStorySerializer(view).data)
        return Response(response)