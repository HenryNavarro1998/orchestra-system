import json
import os
from django.core.management.base import BaseCommand
from ...models import MusicalCenter
from project import settings

class Command(BaseCommand):
    help = 'Seed Musical Center model from a JSON file'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'app', 'data', 'musical_center_data.json')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for item in data:
                MusicalCenter.objects.create(
                    name             = item['name'],
                    type             = item['type'],
                    code             = item['code'],
                    municipality     = item['municipality'],
                    parish           = item['parish'],
                    director_name    = item['director_name'],
                    address          = item['address'],
                )

            self.stdout.write(self.style.SUCCESS('Núcleos creados exitosamente.'))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'No se encontró el archivo en: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocurrió un error: {e}'))