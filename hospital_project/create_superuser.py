# hospital_project/create_superuser.py
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError

def create_admin_user():
    """
    Create a default admin user if it does not exist.
    This runs at WSGI startup. It is intentionally tolerant:
    - If DB isn't available yet, it will silently skip (so startup doesn't fail).
    - It only creates the user if username doesn't exist.
    """
    User = get_user_model()

    # CHANGE THESE BEFORE PRODUCTION if you want other creds.
    username = "admin"
    email = "admin@gmail.com"
    password = "admin@00"

    try:
        if not User.objects.filter(username=username).exists():
            print("Creating default admin user...")
            User.objects.create_superuser(username=username, email=email, password=password)
            print("Default admin created.")
        else:
            print("Default admin already exists; skipping creation.")
    except OperationalError:
        # Database is probably not ready yet (migrations not applied). Skip silently.
        # It will be retried on the next process start.
        pass
