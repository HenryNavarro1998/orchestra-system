import json
import os
from django.core.management.base import BaseCommand
from project import settings
from ...models import AcademicPeriod

class Command(BaseCommand):
    help = 'Seed Academic Periods model from a JSON file'
    
    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'app', 'data', 'academic_period_data.json')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for item in data:
                AcademicPeriod.objects.update_or_create(
                    first_year = item['first_year'],
                    final_year = item['final_year'],
                    defaults={'is_active': item['is_active']}
                )

            self.stdout.write(self.style.SUCCESS('Periodos Académicos creados exitosamente.'))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'No se encontró el archivo en: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocurrió un error: {e}'))