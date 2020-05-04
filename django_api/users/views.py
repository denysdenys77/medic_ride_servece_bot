from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import ServiceUserSerializer
from .models import ServiceUser


@api_view(['DELETE'])
def service_user_delete(request, telegram_id):
    try:
        user = ServiceUser.objects.get(telegram_id=telegram_id)
    except ServiceUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        user.delete()
        return Response(status.HTTP_204_NO_CONTENT)


class ServiceUserViewSet(viewsets.ModelViewSet):
    queryset = ServiceUser.objects.all()
    serializer_class = ServiceUserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = ServiceUser.objects.get(telegram_id=request.data.get('telegram_id'))
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
