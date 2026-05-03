from rest_framework.views import APIView, Response, status
from user_auth.serializers import RegistrationSerializer


class Register(APIView):
    def post(self, request):

        user = RegistrationSerializer(data=request.data)

        if user.is_valid():
            user.save()
            return Response(data=user.data, status=status.HTTP_201_CREATED)

        return Response(data=user.errors, status=status.HTTP_400_BAD_REQUEST)
