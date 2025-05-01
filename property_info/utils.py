import csv
from datetime import datetime, time

from .models import Gravamen, Remate


class TimeUtils:
    @staticmethod
    def parse_time(time_str):
        time_str = time_str.upper().replace('P. M.', 'PM').replace('A. M.', 'AM')
        try:
            return datetime.strptime(time_str, '%I:%M %p').time()
        except ValueError:
            return time(0, 0)



class CsvUtils:
    @staticmethod
    def read_csv(file):
        csv_data = file.read().decode('utf-8').splitlines()
        reader = csv.reader(csv_data)
        header = next(reader)  # Skip header row
        return list(reader)


from django.conf import settings
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

class PropertyInfoData:
    def get_view_liens_detial_data(folio, selectedBuilding):
        gravamen = Gravamen.objects.filter(building__name__icontains=selectedBuilding)
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        file_exists = None
        pdf_files = []

        for pdf_data in gravamen:
            s3_url = pdf_data.get_s3_file_url()
            file_path = pdf_data.get_s3_file_path()
            file_exists = False

            if s3_url:
                try:
                    s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_path)
                    file_exists = True
                except ClientError:
                    file_exists = False

            pdf_files.append({
                'filename': pdf_data.nombre_archivo_pdf,
                'pdf_text': pdf_data.contenido_pdf,
                's3_url': s3_url,
                # 'file_exists': file_exists
            })


        gravamen = Gravamen.objects.filter(building__name__icontains=selectedBuilding)
        print('gravamen', gravamen)
        gravamen_data = list(
            gravamen.values(
                "nombre_archivo_pdf",
                "contenido_pdf",
                "edificio",  # Make sure these fields exist
                "folio",
                'organo_levantamiento',
                'nombre_organo',
                'provincia_organo',
                'num_oficio',
                'fecha_oficio',
                'num_auto',
                'fecha_auto',
                'descripcion',
                'titular_baja_nombre',
                'titular_baja_derecho',
                'fecha_registro',
                'hora_registro',
                'num_entrada',
                'doc_presentado_tipo',
                'doc_presentado_fecha',
                'nombre_juez',
                'derechos_registro',

            )
        )
        return {
            "gravamens": gravamen_data,
            "pdf_raw_data": pdf_files,
            "file_exists": file_exists
        }
    
    def get_view_forclosure_detial_data(selectedBuilding):


        remate = Remate.objects.filter(building__name__icontains=selectedBuilding)
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        file_exists = None
        pdf_files = []

        for pdf_data in remate:
            s3_url = pdf_data.get_s3_file_url()
            file_path = pdf_data.get_s3_file_path()
            file_exists = False

            if s3_url:
                try:
                    s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_path)
                    file_exists = True
                except ClientError:
                    file_exists = False

            pdf_files.append({
                'filename': pdf_data.nombre_archivo_pdf,
                'pdf_text': pdf_data.contenido_pdf,
                's3_url': s3_url,
                # 'file_exists': file_exists
            })



        remate = Remate.objects.filter(building__name__icontains=selectedBuilding)
        print('remate', remate)
        remate_data = list(
            remate.values(
                "nombre_archivo_pdf",
                "contenido_pdf",
                "edificio",
                "folio",
                'organo_remate',
                'nombre_organo',
                'provincia_organo',
                'num_acta_remate',
                'fecha_acta_remate',
                'num_auto',
                'fecha_auto',
                'num_oficio',
                'fecha_oficio',
                'observaciones',
                'titular_baja_nombre',
                'titular_baja_cedula',
                'titular_baja_derecho',
                'nuevo_titular_nombre',
                'nuevo_titular_derecho',
                'fecha_registro',
                'hora_registro',
                'doc_presentado_tipo',
                'doc_presentado_num',
                'doc_presentado_fecha',
                'num_entrada',
                'nombre_juez',
                'derechos_registro',
            )
        )
        return {
            "remates": remate_data,
             "pdf_raw_data": pdf_files,
             "file_exists": file_exists
        }

  