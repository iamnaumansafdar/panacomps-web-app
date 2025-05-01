import csv
from datetime import datetime
from django.core.management.base import BaseCommand

from panaEstate.models import PDFRawData, Folios


class Command(BaseCommand):
    help = 'Import PDF RAW DATA from a CSV file'

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
                    pdf_raw_data = PDFRawData.objects.create(
                        folio=folio,
                        edificio=folio.edificio,
                        filename=row[2],
                        pdf_text=row[3],
                        valor_del_terreno=row[4] if row[4] else None,
                        valor_de_mejoras=row[5] if row[5] else None,
                        valor_del_traspaso=row[6] if row[6] else None,
                        superficie_inicial=row[7],
                        sales_transaction_date=datetime.strptime(row[8], '%d/%m/%Y').date() if row[8] else None,
                        hipoteca=True if row[9] == 'YES' else False,
                        monto=row[10] if row[10] else None,
                        tasa_efectiva=row[11] if row[11] else None,
                        tasa_nominal=row[12] if row[12] else None,
                        interes_anual=row[13] if row[13] else None,
                        feci=row[14] if row[14] else None,
                        interes_anual_feci=row[15] if row[15] else None,
                        nombre=row[16],
                        filing_date=datetime.strptime(row[17], '%d/%m/%Y').date() if row[17] else None
                    )
                    self.stdout.write(self.style.SUCCESS('Successfully imported PDF Data "%s"' % folio.folio))
                except Folios.DoesNotExist:
                    self.stdout.write(self.style.ERROR('Folio "%s" does not exist' % row[0]))
        self.stdout.write(self.style.SUCCESS('Successfully imported all RAW PDF Data'))
