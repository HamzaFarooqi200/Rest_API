from rest_framework import serializers
from .models import CustomUser, Profile, Project, Task, Document, Comment


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "profile_picture", "status", "contact_number"]


class UserSerializer(serializers.ModelSerializer):

    user_profile = ProfileSerializer(required=False)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'user_profile']

        extra_kwargs ={
            'password': {'write_only': True}
            }

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        profile = validated_data.pop('user_profile')
        profile = Profile(
            profile_picture = profile['profile_picture'],
            status = profile['status'],
            contact_number = profile['contact_number'],
            user = user
        )
        profile.save()
        return user


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'team_members']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'project', 'assignee']


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'name', 'description', 'file', 'version', 'project']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'created_at', 'task', 'project']
