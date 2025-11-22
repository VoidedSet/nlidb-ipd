# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # 1. Define the possible roles for RBAC
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Organization Admin'
        ANALYST = 'ANALYST', 'Data Analyst'
        VIEWER = 'VIEWER', 'Viewer'

    # 2. Add the role field to the User model
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.VIEWER
    )

    # 3. FIX: Add unique related_name arguments to prevent clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='tenant_user_set', # <-- UNIQUE NAME
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='tenant_user_permissions_set', # <-- UNIQUE NAME
    )
    
    # Add other utility methods as needed
    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_analyst(self):
        return self.role == self.Role.ANALYST