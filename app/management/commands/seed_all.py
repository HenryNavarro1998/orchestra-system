from django.core.management import BaseCommand, call_command

# Código de color ANSI para cian brillante
COLOR_CIAN = '\033[96m'
# Código para resetear el color de la terminal
RESET_COLOR = '\033[0m'

class Command(BaseCommand):
    help = 'Ejecuta todos los comandos seeder del proyecto.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando la ejecución de todos los seeders...'))

        # Lista de los comandos por ejecutar
        seeders = [
            'seed_instruments',
            'seed_projects',
            'seed_academic_periods',
            'seed_programs',
            'seed_musical_center'
        ]

        for seeder in seeders:
            self.stdout.write(f'{COLOR_CIAN}Ejecutando el seeder: {seeder}{RESET_COLOR}')
            try:
                call_command(seeder)
                self.stdout.write(self.style.SUCCESS(f'Seeder "{seeder}" ejecutado exitosamente.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ocurrió un error al ejecutar el seeder "{seeder}": {e}'))

        self.stdout.write(self.style.SUCCESS('Todos los seeders han sido procesados.'))
