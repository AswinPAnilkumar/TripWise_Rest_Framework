from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from tripmaster.serializers import UserSerializer,TripSerializer
from tripmaster.models import TripDb
from rest_framework import permissions,authentication,serializers
from tripmaster.permissions import OwnerOnly

# Create your views here.
class SignUpView(APIView):
    def post(self,request):
        form_data = request.data
        serializer_instance = UserSerializer(data=form_data)
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response({"Message":"User Registered Successfully"},status=201)
        return Response({"Message":"Invalid Data Provided"},status=400)
    
class UserListView(APIView):
    def get(self,request):
        users = User.objects.all()
        serializer_instance = UserSerializer(users,many=True)
        return Response(data=serializer_instance.data,status=200)
    
class TripListCreateView(APIView):

    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request):
        trips = TripDb.objects.filter(created_by=request.user)
        serializer_instance = TripSerializer(trips,many=True)
        return Response(data=serializer_instance.data)

    def post(self,request):
        form_data = request.data
        serializer_instance = TripSerializer(data=form_data)
        if serializer_instance.is_valid():
            serializer_instance.save(created_by=request.user)
            return Response({"Message":"Trip Created Successfully","Trip Details":serializer_instance.data})
        else:
            return Response(data=serializer_instance.errors)
    
class TripRetrieveUpdateDeleteView(APIView):

    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [OwnerOnly]

    def get(self,request,pk):
        trip_object = get_object_or_404(TripDb,id=pk)
        if trip_object.created_by == request.user:
            serializer_instance = TripSerializer(trip_object)
            return Response(data=serializer_instance.data)
        else:
            raise serializers.ValidationError("You Don't Have Access")

    def put(self,request,pk):
        trip_object = get_object_or_404(TripDb,id=pk)
        if trip_object.created_by != request.user:
            raise serializers.ValidationError("Access Denied")
        form_data = request.data
        serializer_instance = TripSerializer(data=form_data,instance=trip_object)
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response({"Message":"Trip Details Updated Successfully",
                            "Updated Details":serializer_instance.data})
        else:
            return Response(data=serializer_instance.errors)

    def delete(self,request,pk):
        trip_object = get_object_or_404(TripDb,id=pk)
        if trip_object.created_by == request.user:
            trip_object.delete()
            return Response({"Message":"Trip Deleted Successfully"})
        else:
            raise serializers.ValidationError("You don't have access to this data")

