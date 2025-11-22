from django.db import models

from fernet_fields import fields

class DatabaseConnection(models.Model):
    class DatabaseType(models.TextChoices):
        POSTGRES = 'POSTGRES', 'PostgreSQL'
        MYSQL = 'MYSQL', 'MySQL'
    
    name = models.CharField(max_length=100, unique=True, help_text="A friendly name for this connection.")
    db_type = models.CharField(
        max_length=10,
        choices=DatabaseType.choices,
        default=DatabaseType.POSTGRES
    )
    
    # Connection Details
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=100)
    db_name = models.CharField(max_length=100)
        
    # SECURITY CRITICAL: The password must be stored encrypted
    password = fields.EncryptedCharField(max_length=255)
    
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.db_type})"