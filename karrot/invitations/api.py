from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.viewsets import GenericViewSet

from karrot.invitations.models import Invitation
from karrot.invitations.serializers import InvitationSerializer, InvitationAcceptSerializer


class InvitesPerDayThrottle(UserRateThrottle):
    rate = '50/day'


class NotInGroup(BasePermission):
    def has_object_permission(self, request, view, obj):
        return not obj.group.is_member(request.user)


class InvitationsViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    """
    Invitations
    """
    queryset = Invitation.objects
    serializer_class = InvitationSerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filterset_fields = ('group', )
    permission_classes = (IsAuthenticated, )
    throttle_classes = ()

    def get_queryset(self):
        users_groups = self.request.user.groups.user_is_editor(self.request.user)
        return self.queryset.filter(group__in=users_groups, expires_at__gte=timezone.now())

    def get_throttles(self):
        if self.action == 'create':
            self.throttle_classes = (InvitesPerDayThrottle, )
        return super().get_throttles()


class InvitationAcceptViewSet(GenericViewSet):
    queryset = Invitation.objects
    serializer_class = InvitationAcceptSerializer
    permission_classes = (
        IsAuthenticated,
        NotInGroup,
    )
    lookup_field = 'token'

    def get_queryset(self):
        return self.queryset.filter(expires_at__gte=timezone.now())

    @action(detail=True, methods=['POST'])
    def accept(self, request, **kwargs):
        """
        Accept the invitation
        """
        self.check_permissions(request)
        instance = self.get_object()
        self.check_object_permissions(request, instance)

        serializer = self.get_serializer(instance, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
