# Auto-provisions the 'kavya' superuser during deployment
/var/app/venv/*/bin/python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
username = "${DJANGO_SUPERUSER_USERNAME:-kavya}"
password = "${DJANGO_SUPERUSER_PASSWORD:-Admin@12345}"
email = "${DJANGO_SUPERUSER_EMAIL:-kavya@example.com}"
user, created = User.objects.get_or_create(username=username, defaults={'email': email})
user.set_password(password)
user.is_staff = True
user.is_superuser = True
user.is_active = True
user.save()
print(f"Admin user '{username}' configured successfully.")
EOF
