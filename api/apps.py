from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        from api.utils import fetch_and_update_data, save_all_predictions_to_db
        try:
            fetch_and_update_data()
        except Exception as e:
            print(f"Error updating current cases data on server start: {e}")

        try:
            save_all_predictions_to_db()
        except Exception as e:
            print(f"Error updating predictions data on server start: {e}")


