from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import APIView
from .serializer import UserSerializer
from rest_framework import status
from django.http import Http404
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

class UserData(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("USer", request.user)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "user created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
