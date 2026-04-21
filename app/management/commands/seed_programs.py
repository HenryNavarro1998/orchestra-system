import json
import os
from django.core.management.base import BaseCommand

from project import settings
from ...models import MusicalProgram

class Command(BaseCommand):
    help = 'Seed Musical Programs model from a JSON file'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'app', 'data', 'program_data.json')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for item in data:
                MusicalProgram.objects.create(
                    name    = item['name']
                )

            self.stdout.write(self.style.SUCCESS('Programas musicales creados exitosamente.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'No se encontró el archivo en: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocurrió un error: {e}'))