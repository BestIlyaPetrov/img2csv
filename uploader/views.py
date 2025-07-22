from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .forms import ImageUploadForm
import openai
import base64
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')


@login_required
def upload_view(request):
    """Render the upload page."""
    form = ImageUploadForm()
    return render(request, "uploader/upload.html", {"form": form})


@login_required
def process_image_ajax(request):
    """Handle AJAX image uploads and return CSV data as JSON."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    form = ImageUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({"error": "Invalid form"}, status=400)

    image = request.FILES["image"]
    b64_img = base64.b64encode(image.read()).decode("utf-8")

    # OpenAI Vision API using new format
    client = openai.OpenAI(api_key=API_KEY)
    response = client.responses.create(
        model="o4-mini-2025-04-16",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Can you please transcribe this table and return it in csv format?",
                    },
                    {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64_img}"},
                ],
            }
        ],
    )

    csv_data = response.output_text
    print(f"Received CSV data from ChatGPT: {csv_data}")

    return JsonResponse({"csv_data": csv_data})


@login_required
def download_csv(request):
    csv_data = request.session.get("csv_data", "")
    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="table.csv"'
    return response
