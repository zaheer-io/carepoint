from django.http import HttpResponse
from django.contrib.auth import get_user_model

def create_admin_view(request):
    User = get_user_model()

    username = "admin"
    email = "admin@example.com"
    password = "admin@00"

    if User.objects.filter(username=username).exists():
        return HttpResponse("Admin already exists!")

    User.objects.create_superuser(
        username=username, 
        email=email, 
        password=password
    )

    return HttpResponse("Admin user created successfully! DELETE THIS VIEW NOW!")
