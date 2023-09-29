from rest_framework import serializers

from .models import Board, Pin, Comment, Like


class BoardSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Board
        fields = '__all__'



class PinSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    image = serializers.ImageField(read_only=True)
    total_likes = serializers.IntegerField(read_only=True)
    total_comments = serializers.IntegerField(read_only=True)
    board = serializers.StringRelatedField()
    class Meta:
        model = Pin
        fields = '__all__'


class UserFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        queryset = super(UserFilteredPrimaryKeyRelatedField, self).get_queryset()
        if not request or not queryset:
            return None
        return queryset.filter(user=request.user)


class PinCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    board = UserFilteredPrimaryKeyRelatedField(queryset=Board.objects)
    class Meta:
        model = Pin
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    pin = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Comment
        fields = '__all__'


class PinRetrieveSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    image = serializers.ImageField(read_only=True)
    total_likes = serializers.IntegerField(read_only=True)
    total_comments = serializers.IntegerField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Pin
        fields = '__all__'


class LikeSerializer(serializers.ModelSerializer):
    pin = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Like
        fields = '__all__'

