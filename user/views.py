from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import User
from . import serializers


class UserDetailsView(generics.UpdateAPIView, generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserDetailsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return User.objects.get(pk=self.request.user.id)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

