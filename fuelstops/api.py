from rest_framework.generics import GenericAPIView
from .serializers import DestinationSerializer
from rest_framework.response import Response

class DestinationAPI(GenericAPIView) :
    serializer_class = DestinationSerializer

    def post(self, request) :
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resp = serializer.save()

        return Response(resp)


        
