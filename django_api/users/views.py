from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import ServiceUserSerializer
from .models import ServiceUser


class ServiceUserViewSet(viewsets.ModelViewSet):
    queryset = ServiceUser.objects.all()
    serializer_class = ServiceUserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = ServiceUser.objects.get(telegram_id=request.data.get('telegram_id'))
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            service_user = ServiceUser.objects.get(telegram_id=request.data.get('telegram_id'))
            service_user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ServiceUser.DoesNotExist:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
