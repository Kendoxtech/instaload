from django.shortcuts import render

# Create your views here.
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import json
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
from django.http import JsonResponse
from django.shortcuts import render


def fetch_instagram_media(request):
    """Fetch the media URL from the provided Instagram link."""
    if request.method == "POST":
        instagram_url = request.POST.get("url")

        if not instagram_url:
            return JsonResponse({"error": "No URL provided."}, status=400)

        try:
            # Fetch the HTML content of the Instagram page
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(instagram_url, headers=headers)

            if response.status_code != 200:
                return JsonResponse({"error": "Failed to fetch the Instagram URL."}, status=400)

            # Parse the HTML to extract the media URL
            soup = BeautifulSoup(response.text, "html.parser")
            meta_tag = soup.find("meta", property="og:video") or soup.find("meta", property="og:image")

            if not meta_tag:
                return JsonResponse({"error": "Media not found at the provided URL."}, status=404)

            media_url = meta_tag["content"]
            return JsonResponse({"media_url": media_url})

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)


def index(request):
    return render(request, 'downloader.html')





import requests


from django.shortcuts import render
from django.http import JsonResponse
from urllib.parse import urlparse, urlunparse
import requests
from bs4 import BeautifulSoup

def instagram_downloader(request):
    if request.method == "POST":
        instagram_url = request.POST.get("instagram_url")
        print(f"Received URL: {instagram_url}")

        if not instagram_url:
            return JsonResponse({"error": "No URL provided. Please provide a valid Instagram URL."}, status=400)

        # Validate Instagram URL
        parsed_url = urlparse(instagram_url)
        if not (parsed_url.scheme and parsed_url.netloc and "instagram.com" in parsed_url.netloc):
            return JsonResponse({"error": "Invalid Instagram URL. Please provide a valid Instagram URL."}, status=400)

        # Rebuild the URL to ensure it’s clean
        clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, "", "", ""))
        print(f"Cleaned URL: {clean_url}")

        try:
            # Make an HTTP request to the Instagram URL
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(clean_url, headers=headers)
            if response.status_code != 200:
                return JsonResponse({"error": f"Failed to fetch the page. Status code: {response.status_code}"}, status=500)

            # Parse the HTML using BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            print("Page source loaded")

            # Look for the media URL in meta tags
            video_tag = soup.find("meta", property="og:video")
            if video_tag:
                media_url = video_tag["content"]
                media_type = "video"
                print(f"Found video URL: {media_url}")
            else:
                image_tag = soup.find("meta", property="og:image")
                if image_tag:
                    media_url = image_tag["content"]
                    media_type = "image"
                    print(f"Found image URL: {media_url}")
                else:
                    print("Error: No media found on the page.")
                    return JsonResponse({"error": "Could not fetch media. No media found on the Instagram page."}, status=400)

            return JsonResponse({"media_type": media_type, "media_url": media_url}, status=200)

        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

    # If not a POST request, render the downloader template
    print("Rendering downloader template")
    return render(request, "downloader.html")






from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re


@csrf_exempt
def test_download(request):
    if request.method == "GET":
        url = request.GET.get("url")
        media_type = request.GET.get("type", "auto")

        # Validate the URL
        if not url or not re.match(r"^https://(www\.)?instagram\.com/.+", url):
            return JsonResponse({
                "success": False,
                "message": "Invalid Instagram URL. Please provide a valid URL."
            }, status=400)

        # Simulate fetching media
        sample_media = {
            "video": {
                "type": "video",
                "mediaUrl": "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"
            },
            "image": {
                "type": "image",
                "mediaUrl": "https://via.placeholder.com/600"
            },
        }

        # Respond based on the media type
        if media_type == "video":
            return JsonResponse({"success": True, **sample_media["video"]})
        elif media_type == "image":
            return JsonResponse({"success": True, **sample_media["image"]})
        else:
            # Auto-detect defaults to video in this mock
            return JsonResponse({"success": True, **sample_media["video"]})

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)
