# Generated by Django 5.0.4 on 2024-06-04 20:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0002_likedtrack_audio_url_likedtrack_duration_text_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LikedTrack',
        ),
    ]