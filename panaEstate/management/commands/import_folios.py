import csv
from datetime import datetime
from django.core.management.base import BaseCommand

from panaEstate.models import Folios


class Command(BaseCommand):
    help = 'Import folios from a CSV file'

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
                    folio = Folios.objects.create(
                        folio=row[0],
                        modulo=row[1],
                        codigo_ubicacion=row[2],
                        municipio=row[3],
                        edificio=row[4],
                        propietarios=row[5],
                        folio_finca_ficha=row[6],
                        fecha_de_inscripcion=datetime.strptime(row[7], '%d/%m/%Y') if row[7] else None,
                        propietario=row[8],
                        domicilio=row[9],
                        uso_del_suelo=row[10],
                        otro_tipo=row[11],
                        descripcion=row[12],
                        por_edificio=row[13],
                        porcentaje_de_proindiviso=row[14],
                        cedula_catastral=row[15],
                        valor=row[16] if row[16] else None,
                        valor_del_terreno=row[17] if row[17] else None,
                        valor_de_mejoras=row[18] if row[18] else None,
                        valor_del_traspaso=row[19] if row[19] else None,
                        numero_de_plano=row[20],
                        fecha_de_construccion=datetime.strptime(row[21], '%d/%m/%Y') if row[21] else None,
                        fecha_de_ocupacion=datetime.strptime(row[22], '%d/%m/%Y') if row[22] else None,
                        lote=row[23],
                        superficie_inicial=row[24],
                        superficie_resto_libre=row[25],
                        colindancias=row[26],
                        timestamp_added_to_csv=datetime.strptime(row[27],
                                                                 '%Y-%m-%d %H:%M:%S %Z') if row[27] else None,
                        derechos_actos_otras_operaciones=row[28],
                    )
                    self.stdout.write(self.style.SUCCESS('Successfully imported folio "%s"' % folio.folio))
                except Exception as e:
                    self.stdout.write(self.style.ERROR('Error importing folio "%s": %s' % (row[0], e)))
        self.stdout.write(self.style.SUCCESS('Successfully imported all folios'))
