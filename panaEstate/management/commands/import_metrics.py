import csv
from datetime import datetime
from django.core.management.base import BaseCommand

from panaEstate.models import Metrics, Folios


class Command(BaseCommand):
    help = 'Import metrics from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        with open(csv_file, 'r') as f:
            csv_file = csv.reader(f, delimiter=',')
            # skip first row
            next(csv_file)
            for row in csv_file:
                try:
                    folio = Folios.objects.get(folio=row[0])
                    metric = Metrics.objects.create(
                        folio=folio,
                        codigo_ubicacion=row[1],
                        municipio=row[2],
                        edificio=folio.edificio,
                        fecha_de_construccion=datetime.strptime(row[4], '%d/%m/%Y').date() if row[4] else None,
                        fecha_de_ocupacion=datetime.strptime(row[5], '%d/%m/%Y').date() if row[5] else None,
                        propietarios=row[6],
                        domicilio=row[7],
                        sales_transaction_date=datetime.strptime(row[8], '%d/%m/%Y').date() if row[8] else None,
                        valor=row[9] if row[9] else None,
                        valor_del_terreno=row[10] if row[10] else None,
                        valor_de_mejoras=row[11] if row[11] else None,
                        valor_del_traspaso=row[12] if row[12] else None,
                        superficie_inicial=row[13],
                        price_per_square_meter=row[14] if row[14] else None,
                        hipoteca=True if row[15] == 'YES' else False,
                        monto=row[16] if row[16] else None,
                        tasa_efectiva=row[17] if row[17] else None,
                        tasa_nominal=row[18] if row[18] else None,
                        interes_anual=row[19] if row[19] else None,
                        feci=row[20] if row[20] else None,
                        interes_anual_feci=row[21] if row[21] else None,
                        nombre=row[22],
                        timestamp=datetime.strptime(row[23], '%Y-%m-%d %H:%M:%S %Z') if row[23] else None,
                        uso_del_suelo=row[24]
                    )
                    self.stdout.write(self.style.SUCCESS('Successfully imported Metric "%s"' % folio.folio))
                except Folios.DoesNotExist:
                    self.stdout.write(self.style.ERROR('Folio "%s" does not exist' % row[0]))
        self.stdout.write(self.style.SUCCESS('Successfully imported all Metrics'))
