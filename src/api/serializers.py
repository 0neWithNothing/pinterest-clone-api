from rest_framework import serializers
from django.core.paginator import Paginator
from rest_framework import status

from .models import Board, Pin, Comment, Like


class ProfileBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        exclude = ('description', 'user', )


class PinSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)
    class Meta:
        model = Pin
        fields = ['id', 'image', 'title']


class BoardSerializer(serializers.ModelSerializer):
    pins = serializers.SerializerMethodField('paginated_pins')
    class Meta:
        model = Board
        exclude = ('user', )


    def paginated_pins(self, obj):
        page_size = 10
        paginator = Paginator(obj.pins.all(), page_size)
        page = self.context['request'].query_params.get('page') or 1
        try:
            pins_in_board = paginator.page(page)
        except:
            raise serializers.ValidationError({'detail': 'Invalid page.'})
        serializer = PinSerializer(pins_in_board, many=True, read_only=True)

        return serializer.data


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
    board = serializers.StringRelatedField()
    comments = serializers.SerializerMethodField('paginated_comments')
    class Meta:
        model = Pin
        fields = '__all__'


    def paginated_comments(self, obj):
        page_size = 20
        paginator = Paginator(obj.comments.all(), page_size)
        page = self.context['request'].query_params.get('page') or 1
        try:
            comments_in_pin = paginator.page(page)
        except:
            raise serializers.ValidationError({'detail': 'Invalid page.'})
        serializer = CommentSerializer(comments_in_pin, many=True, read_only=True)

        return serializer.data


class LikeSerializer(serializers.ModelSerializer):
    pin = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Like
        fields = '__all__'

