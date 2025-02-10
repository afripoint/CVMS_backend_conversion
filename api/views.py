from django.http import JsonResponse

def health_check(request):
    """
    A simple health check endpoint to verify the application is running.
    """
    return JsonResponse({"status": "ok"})