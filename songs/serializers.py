from rest_framework import serializers
from .models import (
    User, Song, Library, SongPrompt,
    AIGenerationRequest, SharedSong, PlaybackSession, Draft,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'user_id', 'google_id', 'email',
            'display_name', 'session_token',
        ]
        read_only_fields = ['user_id']


class PlaybackSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaybackSession
        fields = [
            'id', 'session_id', 'current_position',
            'loop_start', 'loop_end', 'equalizer_settings',
        ]
        read_only_fields = ['session_id']


class SongSerializer(serializers.ModelSerializer):
    # Expose UUIDs of related objects for readability
    user_id = serializers.PrimaryKeyRelatedField(
        source='user', queryset=User.objects.all()
    )
    playback_session_id = serializers.PrimaryKeyRelatedField(
        source='playback_session',
        queryset=PlaybackSession.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Song
        fields = [
            'id', 'song_id', 'user_id', 'playback_session_id',
            'title', 'audio_file_url', 'generation_status',
            'created_at', 'is_favorite', 'is_draft', 'share_link',
        ]
        read_only_fields = ['song_id', 'created_at']


class LibrarySerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source='user', queryset=User.objects.all()
    )
    song_ids = serializers.PrimaryKeyRelatedField(
        source='songs',
        queryset=Song.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Library
        fields = [
            'id', 'user_id', 'song_ids',
            'filter_criteria', 'total_count',
        ]
        read_only_fields = ['total_count']

    def create(self, validated_data):
        songs = validated_data.pop('songs', [])
        library = Library.objects.create(**validated_data)
        library.songs.set(songs)
        library.sync_total_count()
        return library

    def update(self, instance, validated_data):
        songs = validated_data.pop('songs', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if songs is not None:
            instance.songs.set(songs)
            instance.sync_total_count()
        return instance


class SongPromptSerializer(serializers.ModelSerializer):
    song_id = serializers.PrimaryKeyRelatedField(
        source='song', queryset=Song.objects.all()
    )

    class Meta:
        model = SongPrompt
        fields = [
            'id', 'prompt_id', 'song_id', 'title',
            'occasion', 'mood_and_tone', 'singer_tone', 'description',
        ]
        read_only_fields = ['prompt_id']


class AIGenerationRequestSerializer(serializers.ModelSerializer):
    prompt_id = serializers.PrimaryKeyRelatedField(
        source='prompt', queryset=SongPrompt.objects.all()
    )

    class Meta:
        model = AIGenerationRequest
        fields = [
            'id', 'request_id', 'prompt_id',
            'submitted_at', 'status', 'error_message',
        ]
        read_only_fields = ['request_id', 'submitted_at']


class SharedSongSerializer(serializers.ModelSerializer):
    song_id = serializers.PrimaryKeyRelatedField(
        source='song', queryset=Song.objects.all()
    )

    class Meta:
        model = SharedSong
        fields = [
            'id', 'share_id', 'song_id',
            'share_link', 'shared_at', 'accessible_by_guest',
        ]
        read_only_fields = ['share_id', 'shared_at']


class DraftSerializer(serializers.ModelSerializer):
    song_id = serializers.PrimaryKeyRelatedField(
        source='song', queryset=Song.objects.all()
    )

    class Meta:
        model = Draft
        fields = [
            'id', 'draft_id', 'song_id',
            'saved_at', 'is_submitted', 'retention_policy',
        ]
        read_only_fields = ['draft_id', 'saved_at']
