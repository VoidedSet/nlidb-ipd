from rest_framework import serializers
from .models import DatabaseConnection

class DatabaseConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseConnection
        # Note: 'password' is included here. EncryptedCharField handles encryption automatically on save.
        fields = ['id', 'name', 'db_type', 'host', 'port', 'username', 'password', 'is_active']
        read_only_fields = ['is_active']
        # Hide the sensitive password field from responses
        extra_kwargs = {
            'password': {'write_only': True}
        }