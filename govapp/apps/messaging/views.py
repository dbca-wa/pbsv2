import logging

from django.conf import settings
from drf_spectacular import utils
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from govapp.apps.messaging import serializers
from govapp.apps.messaging.models import Message, MessageBatch
from govapp.permissions import HasObjectPermission, IsDjangoAdmin, IsPBSAdmin

logger = logging.getLogger(__name__)


@utils.extend_schema(tags=["Messaging - Message Batches"])
class MessageBatchViewSet(viewsets.ReadOnlyModelViewSet):
    """Message Batch ViewSet."""

    queryset = MessageBatch.objects.all()
    serializer_class = serializers.MessageBatchSerializer
    permission_classes = [IsDjangoAdmin | IsPBSAdmin]


@utils.extend_schema(tags=["Messaging - Messages"])
class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    """Message Batch ViewSet."""

    queryset = Message.objects.all()
    serializer_class = serializers.MessageSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()
        return self.queryset.filter(agency=self.request.user.agency)

    @action(detail=False, methods=["get"])
    def latest(self, request):
        """Get the latest messages."""
        queryset = (
            self.get_queryset()
            .filter(user=request.user)
            .exclude(dismissed=True)
            .order_by("-created")[: settings.MESSAGING_LATEST_MESSAGES_COUNT]
        )
        serializer = self.get_serializer(queryset, many=True)

        # For small querysets it's nice to be able to delete by key on the front end
        data = {f"{row['id']}": row for row in serializer.data}

        return Response(data)

    @action(detail=True, methods=["PATCH"], permission_classes=[HasObjectPermission])
    def dismiss(self, request, *args, **kwargs):
        """Dismisses a message."""
        instance = self.get_object()
        instance.dismissed = True
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
