from django.db import models
from django.contrib.auth.models import User

class LikedSong(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track_id = models.CharField(max_length=100)
    track_name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    cover_url = models.URLField()
    duration = models.CharField(max_length=10)
    
    def __str__(self) :
        return f"{self.track_name} by {self.artist_name}"
       