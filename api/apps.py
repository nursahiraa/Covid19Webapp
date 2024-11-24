from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        from api.utils import fetch_and_update_data
        try:
            fetch_and_update_data()
        except Exception as e:
            print(f"Error updating data on server start: {e}")
