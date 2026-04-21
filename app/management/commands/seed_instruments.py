import json
import os
from django.core.management.base import BaseCommand
from project import settings
from ...models import Instrument

class Command(BaseCommand):
    help = 'Seed Instrument model from a JSON file'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'app', 'data', 'instrument_data.json')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for item in data:
                Instrument.objects.create(
                    name     = item['name'],
                    category = item['category']
            )

            self.stdout.write(self.style.SUCCESS('Instrumentos creados exitosamente.'))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'No se encontró el archivo en: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocurrió un error: {e}'))