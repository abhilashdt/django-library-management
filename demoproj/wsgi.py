import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demoproj.settings")
application = get_wsgi_application()

# Auto-migrate database tables on Elastic Beanstalk if postdeploy hooks were skipped
try:
    from django.core.management import call_command
    from django.db import connection

    if "catalog_book" not in connection.introspection.table_names():
        call_command("migrate", interactive=False)
except Exception:  # pylint: disable=broad-exception-caught
    pass
