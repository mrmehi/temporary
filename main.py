from django.core.management import execute_from_command_line
import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'myproject.settings')

# Initialize the Django environment
django.setup()

if __name__ == "__main__":
    # Run the development server
    print('Starting Django development server...')
