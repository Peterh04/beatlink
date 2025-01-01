from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest,JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
import requests
from bs4 import BeautifulSoup as bs
import re
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
from .models import LikedSong
from django.views.decorators.csrf import csrf_exempt
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Create your views here.
def top_artists():
    url = f"{os.getenv('API_BASE_URL')}chart/artists/top"

    querystring = {"type":"weekly"}

    headers = {
        "x-rapidapi-key": f"{os.getenv("API_KEY")}",
        "x-rapidapi-host": f"{os.getenv('RAPID_API_HOST')}"
    }

    response = requests.get(url, headers=headers, params=querystring)
    response_data = response.json()
    
    artists_info = []
    
    if 'artists' in response_data:
        for artist in response_data['artists']:
            name = artist.get('name', 'No name')
            artist_id = artist.get('id','No Id' )
            avatar_url = artist.get('visuals', {}).get('avatar', [{}])[0].get('url', 'No Url')
            artists_info.append(name, avatar_url, artist_id)
            
    return artists_info

def top_tracks():
    

    url = f"{os.getenv('API_BASE_URL')}chart/tracks/top"

    querystring = {"type":"weekly"}

    headers = {
        "x-rapidapi-key": f"{os.getenv("API_KEY")}",
        "x-rapidapi-host": f"{os.getenv('RAPID_API_HOST')}"
    }

    response = requests.get(url, headers=headers, params=querystring)
    
    data = response.json()
    
    track_details = []

    if 'tracks' in data:
        shortened_data = data['tracks'][:18]
        
        for track in shortened_data:
            track_id = track['id']
            track_name = track['name']
            artist_name = track['artists'][0]['name'] if track['artists'] else None
            cover_url = track['album']['cover'][0]['url'] if track['album']['cover'] else None

            track_details.append({
                'id': track_id,
                'name': track_name,
                'artist': artist_name,
                'cover_url': cover_url
            })

    else:
        print("track not foun in response")

    return track_details


    

@login_required(login_url='login')
def index(request):
    artists_info = top_artists()
    
    context = {
        'artists_info' : artists_info
    }
    return render(request, 'index.html', context)

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = auth.authenticate(username = username, password = password)
        
        if user is not None:
            #log user in
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Check the credentials again!')
            return redirect('login')
    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password != password2:
            messages.info(request,'Passsword does not match!')
            return redirect('signup')
        else:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email does exist, Please Login')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already taken!')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                 
                #log user in
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                return redirect('/')
    else:
        return render(request, 'signup.html')
    
@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')


def get_track_image(track_id, track_name):
    url = 'https://open.spotify.com/track/' + track_id
    r = requests.get(url)
    soup = bs(r.content, 'html.parser')
    image_links_html = soup.find('img', {'alt': track_name})
    if image_links_html:
        image_links = image_links_html['srcset']
    else:
        image_links = ''
    match = re.search(r'https:\/\/i\.scdn\.co\/image\/[a-zA-Z0-9]+ 640w', image_links)

    if match:
        url_640w = match.group().rstrip(' 640w')
    else:
        url_640w = ''

    return url_640w

def get_audio_details(query):


    url = f"{os.getenv('API_BASE_URL')}track/download/soundcloud"

    querystring = {"track": query}

    headers = {
        "x-rapidapi-key": f"{os.getenv("API_KEY")}",
        "x-rapidapi-host": f"{os.getenv('RAPID_API_HOST')}"
    }

    response = requests.get(url, headers=headers, params=querystring)
    audio_details = []
    
    if response.status_code == 200:
        response_data = response.json()

        if 'soundcloudTrack' in response_data and 'audio' in response_data['soundcloudTrack']:
            audio_list = response_data['soundcloudTrack']['audio']
            if audio_list:
                first_audio_url = audio_list[0]['url']
                duration_text = audio_list[0]['durationText']

                audio_details.append(first_audio_url)
                audio_details.append(duration_text)
                print(first_audio_url)
            else:
                print("No audio data availble")
        else:
            print("No 'youtubeVideo' or 'audio' key found")
    else:
        print("Failed to fetch data")

    return audio_details

   
    
@login_required(login_url='login')
def music(request, pk):
    track_id = pk

    url = f"{os.getenv('API_BASE_URL')}track/metadata"
    querystring = {"trackId": track_id}


    headers = {
        "x-rapidapi-key": f"{os.getenv("API_KEY")}",
        "x-rapidapi-host": f"{os.getenv('RAPID_API_HOST')}"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        # extrack track_name, artist_name
        track_name = data.get("name")
        artists_list = data.get("artists", [])
        first_artist_name = artists_list[0].get("name") if artists_list else "No artist found"

        audio_details_query = track_name + first_artist_name
        audio_details = get_audio_details(audio_details_query)
        audio_url = audio_details[0]
        duration_text = audio_details[1]

        track_image = get_track_image(track_id, track_name)

        context = {
            'track_id': track_id,  # Include track_id in the context
            'track_name': track_name,
            'artist_name': first_artist_name,
            'audio_url': audio_url,
            'duration_text': duration_text,
            'track_image': track_image,
        }
        return render(request, 'music.html', context)
    
    else:
        # Handle the case where the API request fails
        return HttpResponse("Failed to fetch track metadata", status=response.status_code)


   
@login_required(login_url='login')
def search(request):
    if request.method == 'POST':
        search_query = request.POST['search_query']
        
        url = f"{os.getenv('API_BASE_URL')}search"

        querystring = {"term":search_query, 'type': 'track'}

        headers = {
            "x-rapidapi-key": f"{os.getenv("API_KEY")}",
            "x-rapidapi-host": f"{os.getenv('RAPID_API_HOST')}"
        }

        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            data = response.json()

            search_results_count = data["tracks"]["totalCount"]
            tracks = data["tracks"]["items"]
            
            track_list = []

            for track in tracks:
                track_name = track["name"]
                artist_name = track["artists"][0]["name"]
                duration = track["durationText"]
                trackid = track["id"]
                track_image= track["album"]["cover"][0]["url"]
                
                
                track_list.append({
                    'track_name': track_name,
                    'artist_name': artist_name,
                    'duration': duration,
                    'trackid': trackid,
                    'track_image': track_image
                    
                    
                   
                })
        context = {
            # 'search_results_count': search_results_count,
            'track_list': track_list,
        }

        return render(request, 'search.html', context)
    else:
       return render(request, 'search.html')

def settings(request):
    return render(request, 'settings.html')

def update_credentials(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_name = request.POST.get('new_name', '')
        new_email = request.POST.get('new_email', '')
        new_password = request.POST.get('new_password', '')
        
        user = request.user
        
        # Check if the current password matches
        if not check_password(current_password, user.password):
            # If the current password doesn't match, log the user out and redirect to login page
            auth.logout(request)
            return redirect('login')
        
        # Update user information if provided
        if new_name:
            user.username = new_name
        if new_email:
            user.email = new_email
        if new_password:
            user.set_password(new_password)  # Set the new password
            # After changing the password, it's recommended to update the session to keep the user logged in
            user.save(update_fields=['password'])  # Save only the password field
            update_session_auth_hash(request, user)  # Update session
        user.save()
        
        return redirect('/')
    else:
        return HttpResponseBadRequest("Invalid request method")
    

@csrf_exempt
def like_song(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        track_id = data.get('track_id')

        # Assuming you have a model LikedSong with a user and track_id field
        liked_song, created = LikedSong.objects.get_or_create(
            user=request.user,
            track_id=track_id,
            defaults={
                'track_name': data.get('track_name'),
                'artist_name': data.get('artist_name'),
                'cover_url': data.get('cover_url'),
                'duration': data.get('duration'),
            }
        )

        if created:
            return JsonResponse({'status': 'liked'})
        else:
            return JsonResponse({'status': 'already_liked'})

    return JsonResponse({'status': 'error'})


@login_required(login_url='login')
def liked_songs(request):
    liked_songs = LikedSong.objects.filter(user=request.user)
    context = {
        'liked_songs': liked_songs
    }
    return render(request, 'liked_songs.html', context)

@csrf_exempt
def delete_song(request, track_id):
    if request.method == 'DELETE':
        try:
            song = LikedSong.objects.get(track_id=track_id)
            song.delete()
            return JsonResponse({'message': 'Song deleted successfully'}, status=200)
        except LikedSong.DoesNotExist:
            return JsonResponse({'error': 'Song not found'}, status=404)
    else:
        return JsonResponse({'error': 'Only DELETE requests are allowed'}, status=405)