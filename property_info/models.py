from django.db import models
import uuid
from panaEstate.models import Building
from django.conf import settings

#Lien
class Gravamen(models.Model):
    guid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, null=True, blank=True) 
    folio = models.IntegerField()
    edificio = models.CharField(max_length=255)
    organo_levantamiento = models.CharField(max_length=255)
    nombre_organo = models.CharField(max_length=255)
    provincia_organo = models.CharField(max_length=255)
    num_oficio = models.CharField(max_length=255)
    fecha_oficio = models.DateField()
    num_auto = models.CharField(max_length=255)
    fecha_auto = models.DateField()
    descripcion = models.TextField()
    titular_baja_nombre = models.CharField(max_length=255)
    titular_baja_derecho = models.CharField(max_length=500)
    fecha_registro = models.DateField()
    hora_registro = models.TimeField()
    num_entrada = models.CharField(max_length=255)
    doc_presentado_tipo = models.CharField(max_length=255)
    doc_presentado_fecha = models.DateField()
    nombre_juez = models.CharField(max_length=255)
    derechos_registro = models.CharField(max_length=255)
    nombre_archivo_pdf = models.CharField(max_length=255)
    contenido_pdf = models.TextField()

    class Meta:
        verbose_name = "Gravamenes"  # Singular form
        verbose_name_plural = "Gravamenes"  # Plural form


    def get_s3_file_path(self):
        if self.building and self.folio and self.nombre_archivo_pdf:
            return f'{self.building.guid}/Folio_PDFs/{self.folio}/{self.nombre_archivo_pdf}'
            # return 'ChIJfX6YVraprI8R2IiULzzdk9o/Folio_PDFs/30459587/(Traslado_de_la_matriz_(INMUEBLE)_PANAMÁ_Código_de_Ubicación_8703,_Folio_Real_N__236_(F))_Asiento_Electrónico_N__6_(FIDEICOMISO)_Entrada_452215_2018_(0)_12-11-2018.pdf'
        return None    

    def get_s3_file_url(self):
        file_path = self.get_s3_file_path()
        if file_path:
            full_url = construct_s3_url(file_path) 
            print(full_url, 'full_url')
            return full_url
        return None


def construct_s3_url(file_path):
    full_url = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_path}'
    return full_url    

class Remate(models.Model):
    guid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, null=True, blank=True) 
    folio = models.IntegerField()
    edificio = models.CharField(max_length=255)
    organo_remate = models.CharField(max_length=255)
    nombre_organo = models.CharField(max_length=255)
    provincia_organo = models.CharField(max_length=255)
    num_acta_remate = models.CharField(max_length=255)
    fecha_acta_remate = models.DateField()
    num_auto = models.CharField(max_length=255)
    fecha_auto = models.DateField()
    num_oficio = models.CharField(max_length=255)
    fecha_oficio = models.DateField()
    observaciones = models.TextField()
    titular_baja_nombre = models.CharField(max_length=255)
    titular_baja_cedula = models.CharField(max_length=255)
    titular_baja_derecho = models.CharField(max_length=500)
    nuevo_titular_nombre = models.CharField(max_length=255)
    nuevo_titular_derecho = models.CharField(max_length=500)
    fecha_registro = models.DateField()
    hora_registro = models.TimeField()
    doc_presentado_tipo = models.CharField(max_length=255)
    doc_presentado_num = models.CharField(max_length=255)
    doc_presentado_fecha = models.DateField()
    num_entrada = models.CharField(max_length=255)
    nombre_juez = models.CharField(max_length=255)
    derechos_registro = models.CharField(max_length=255)
    nombre_archivo_pdf = models.CharField(max_length=255)
    contenido_pdf = models.TextField()


    def get_s3_file_path(self):
        if self.building and self.folio and self.nombre_archivo_pdf:
            return f'{self.building.guid}/Folio_PDFs/{self.folio}/{self.nombre_archivo_pdf}'
            # return 'ChIJfX6YVraprI8R2IiULzzdk9o/Folio_PDFs/30459587/(Traslado_de_la_matriz_(INMUEBLE)_PANAMÁ_Código_de_Ubicación_8703,_Folio_Real_N__236_(F))_Asiento_Electrónico_N__6_(FIDEICOMISO)_Entrada_452215_2018_(0)_12-11-2018.pdf'
        return None    

    def get_s3_file_url(self):
        file_path = self.get_s3_file_path()
        if file_path:
            full_url = construct_s3_url(file_path) 
            print(full_url, 'full_url')
            return full_url
        return None


def construct_s3_url(file_path):
    full_url = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_path}'
    return full_url
