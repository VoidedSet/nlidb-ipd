# tenants/models.py
from django_tenants.models import TenantMixin, DomainMixin
from django.db import models

class Organization(TenantMixin):
    # Tenant model will be stored in the public schema
    name = models.CharField(max_length=100, unique=True)
    paid_until = models.DateField()
    on_trial = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)

    # default true, so all schemas get automatically created
    auto_create_schema = True 
    # default true, so all schemas get automatically deleted
    auto_drop_schema = True

    def __str__(self):
        return self.name

class Domain(DomainMixin):
    # This model maps a hostname to a tenant (Organization)
    # e.g., client1.querify.com -> Organization(name='Client 1')
    def __str__(self):
        return self.domain