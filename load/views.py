from django.shortcuts import render

# Create your views here.


from django.views.decorators.csrf import csrf_exempt

import json



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


from django.http import JsonResponse
from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import json
import re


def extract_media_id(instagram_url):
    match = re.search(r'/p/([^/]+)', instagram_url)
    if match:
        return match.group(1)
    return None


def instagram_downloader(request):
    if request.method == "POST":
        instagram_url = request.POST.get("instagram_url")
        print(f"Received URL: {instagram_url}")

        if not instagram_url:
            print("Error: No URL provided")
            return JsonResponse({"error": "No URL provided. Please provide a valid Instagram URL."}, status=400)

        # Extract media ID from the Instagram URL
        media_id = extract_media_id(instagram_url)
        print(f"Extracted media ID: {media_id}")

        if not media_id:
            print(f"Invalid Instagram URL: {instagram_url}")
            return JsonResponse({"error": "Invalid Instagram URL. Could not extract media ID."}, status=400)

        try:
            # Send a GET request to fetch the page content
            response = requests.get(instagram_url)
            print(f"Request status code: {response.status_code}")
            if response.status_code != 200:
                return JsonResponse({"error": "Failed to fetch Instagram page."}, status=400)

            # Parse the page with BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            print("Page source loaded")

            # Find the JSON embedded in the page containing media URLs
            shared_data = soup.find("script", {"type": "text/javascript"})
            if shared_data:
                shared_data = shared_data.string
                # Look for the JSON that contains media data
                match = re.search(r'window\._sharedData = ({.*?});</script>', shared_data)
                if match:
                    json_data = match.group(1)
                    data = json.loads(json_data)
                    print(f"Fetched JSON data: {data}")

                    media_info = data['entry_data']['PostPage'][0]['graphql']['shortcode_media']
                    if 'image_versions2' in media_info:
                        media_url = media_info['image_versions2']['candidates'][0]['url']
                        media_type = 'image'
                        print(f"Found image URL: {media_url}")
                    elif 'video_versions' in media_info:
                        media_url = media_info['video_versions'][0]['url']
                        media_type = 'video'
                        print(f"Found video URL: {media_url}")
                    else:
                        print("Error: Unsupported media type.")
                        return JsonResponse({"error": "Unsupported media type."}, status=400)

                    return JsonResponse({"media_type": media_type, "media_url": media_url}, status=200)
                else:
                    print("Error: Could not find media data.")
                    return JsonResponse({"error": "Could not find media. Check the URL and try again."}, status=400)

        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

    print("Rendering downloader template")
    return render(request, "downloader.html")


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
