from django.db import models
from django.utils.text import slugify


class Department(models.Model):
    """Hospital department model."""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='departments/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def doctor_count(self):
        return self.doctors.filter(user__is_approved=True).count()
    
    @property
    def active_doctors(self):
        return self.doctors.filter(user__is_approved=True, user__is_active=True)
