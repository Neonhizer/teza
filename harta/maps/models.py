from django.db import models


class Location(models.Model):
    n = models.CharField(max_length=200)
    descriptioamen = models.TextField()
    address = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    event_name = models.CharField(max_length=200, blank=True, null=True)
    event_description = models.TextField(blank=True, null=True)
    

    def __str__(self):
        return self.name
class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved')], default='pending')

    def __str__(self):
        return self.title


class Imagine(models.Model):
    nume = models.CharField(max_length=255)
    imagine = models.BinaryField()

    def __str__(self):
        return self.nume
    

class ChatHistory(models.Model):
    user_message = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

