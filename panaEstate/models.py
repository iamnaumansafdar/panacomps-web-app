from django.db import models
from django.conf import settings
import urllib.parse
from urllib.parse import quote
# Create your models here.


class BarriosEdificios(models.Model):
    guid = models.BigIntegerField(null=True, blank=True, unique=True)
    nombre_barrio = models.CharField(max_length=255, null=True, blank=True, unique=True)
    descripcion_barrio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_barrio
    
    class Meta:
        db_table = "BarriosEdificios"
        verbose_name_plural = "Barrios"

class Building(models.Model):
    guid = models.BigIntegerField(null=True, blank=True, unique=True)
    nombre_barrio = models.ForeignKey(BarriosEdificios, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    street = models.CharField(max_length=255, blank=True, null=True)
    address_1 = models.CharField(max_length=255, blank=True, null=True)
    address_2 = models.CharField(max_length=255, blank=True, null=True)
    district_id = models.IntegerField(blank=True, null=True)
    city_id = models.IntegerField(blank=True, null=True)
    location_id = models.IntegerField(blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    telephone_nr = models.CharField(max_length=50, blank=True, null=True)
    mobile_nr = models.CharField(max_length=50, blank=True, null=True)
    fax_nr = models.CharField(max_length=50, blank=True, null=True)
    youtube_id = models.CharField(max_length=50, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    units = models.IntegerField(blank=True, null=True)
    stars = models.IntegerField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    floors_count = models.IntegerField(blank=True, null=True)
    construction_year = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    gmaps_place_id = models.CharField(max_length=255)
    building_type = models.CharField(max_length=50, blank=True, null=True)
    developer = models.CharField(max_length=255, blank=True, null=True)
    amenities = models.CharField(max_length=255, blank=True, null=True)
    occupancy_permit_date = models.DateField(blank=True, null=True)
    registry_code = models.CharField(max_length=50, blank=True, null=True)
    energy_certification = models.CharField(max_length=50, blank=True, null=True)
    security_features = models.CharField(max_length=255, blank=True, null=True)
    owner_association = models.CharField(max_length=255, blank=True, null=True)
    rentals_allowed = models.BooleanField(default=False)
    rental_type = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return str(self.name)
    

    def generate_guid(self):
        base = 281
        building_name = self.name.lower()  # Convert building name to lowercase
        name_hash = sum(ord(char) for char in building_name) % 10000  # Sum of ASCII values, then mod 10000
        guid = (base * 10000) + name_hash  # Generate GUID using the formula
        return guid

    def save(self, *args, **kwargs):
        if not self.guid:
           self.guid = self.generate_guid()
        super(Building, self).save(*args, **kwargs)


class Folios(models.Model):
    folio = models.BigIntegerField()  # Folio number
    building = models.ForeignKey(Building, on_delete=models.CASCADE, null=True, blank=True) 
    modulo = models.TextField(blank=True, null=True)  # Module
    codigo_ubicacion = models.IntegerField(blank=True, null=True)  # Location code
    municipio = models.TextField(blank=True, null=True)  # Municipality
    edificio = models.TextField()  # Building
    propietarios = models.TextField(blank=True, null=True)  # Owners
    folio_finca_ficha = models.TextField(blank=True, null=True)  # Farm file folio
    fecha_de_inscripcion = models.DateField(blank=True, null=True)  # Registration date
    propietario = models.TextField(blank=True, null=True)  # Owner
    domicilio = models.TextField(blank=True, null=True)  # Address
    uso_del_suelo = models.TextField(blank=True, null=True)  # Land use
    otro_tipo = models.TextField(blank=True, null=True)  # Other type
    descripcion = models.TextField(blank=True, null=True)  # Description
    por_edificio = models.TextField(blank=True, null=True)  # By building
    porcentaje_de_proindiviso = models.TextField(
        blank=True, null=True
    )  # Percentage of indivisible
    cedula_catastral = models.TextField(blank=True, null=True)  # Cadastral certificate
    valor = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Value
    valor_del_terreno = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Land value /sale price/amount
    valor_de_mejoras = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Improvement value
    valor_del_traspaso = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Transfer value
    numero_de_plano = models.TextField(blank=True, null=True)  # Plan number
    fecha_de_construccion = models.DateField(blank=True, null=True)  # Construction date
    fecha_de_ocupacion = models.DateField(blank=True, null=True)  # Occupation date
    lote = models.TextField(blank=True, null=True)  # Lot
    superficie_inicial = models.TextField(
        blank=True, null=True
    )  # Initial area / square meter
    superficie_resto_libre = models.TextField(
        blank=True, null=True
    )  # Remaining free area
    colindancias = models.TextField(blank=True, null=True)  # Boundaries
    timestamp_added_to_csv = models.DateTimeField(
        blank=True, null=True
    )  # Timestamp added to CSV
    derechos_actos_otras_operaciones = models.TextField(
        blank=True, null=True
    )  # Rights, acts, and other operations

    class Meta:
        unique_together = (("folio", "edificio"),)
        db_table = "Folios"
        verbose_name_plural = "Folios"

    def __str__(self):
        return str(self.folio)



class Metrics(models.Model):
    folio = models.ForeignKey(Folios, on_delete=models.CASCADE)  # folio
    building = models.ForeignKey(Building, on_delete=models.CASCADE, null=True, blank=True)  # folio
    codigo_ubicacion = models.IntegerField(blank=True, null=True)  # Location code
    municipio = models.TextField(blank=True, null=True)  # Municipality
    edificio = models.TextField()  # Building
    fecha_de_construccion = models.DateField(blank=True, null=True)  # Construction date
    fecha_de_ocupacion = models.DateField(blank=True, null=True)  # Occupation date
    propietarios = models.TextField(blank=True, null=True)  # Owners
    domicilio = models.TextField(blank=True, null=True)  # Address
    sales_transaction_date = models.DateField(
        blank=True, null=True
    )  # Sales Transaction Date
    valor = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Value
    valor_del_terreno = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Land value
    valor_de_mejoras = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Improvement value
    valor_del_traspaso = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Transfer value  / Sales Amount
    superficie_inicial = models.TextField(
        blank=True, null=True
    )  # Initial area / square meter
    price_per_square_meter = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Price per square meter
    hipoteca = models.BooleanField(blank=True, null=True)  # Mortgage
    monto = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Amount /Sales Amount
    tasa_efectiva = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Effective rate
    tasa_nominal = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Nominal rate
    interes_anual = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Annual interest
    feci = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # FECI
    interes_anual_feci = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Annual interest + FECI
    nombre = models.TextField(blank=True, null=True)  # Name / Lending Entity
    timestamp = models.DateTimeField(blank=True, null=True)  # Timestamp /Date Added
    uso_del_suelo = models.TextField(blank=True, null=True)  # Land use

    class Meta:
        db_table = "Metrics"
        unique_together = (("folio", "edificio"),)
        verbose_name_plural = "Metrics"

    def __str__(self):
        return str(self.edificio)


class PDFRawData(models.Model):
    folio = models.ForeignKey(Folios, on_delete=models.CASCADE)  # Folio
    building = models.ForeignKey(Building, on_delete=models.CASCADE, null=True, blank=True) 
    edificio = models.TextField()  # Building
    filename = models.TextField(blank=True, null=True)  # Filename
    pdf_text = models.TextField(blank=True, null=True)  # pdf text
    valor_del_terreno = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Land value
    valor_de_mejoras = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Improvement value
    valor_del_traspaso = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Transfer value
    superficie_inicial = models.TextField(blank=True, null=True)  # Initial area
    sales_transaction_date = models.DateField(
        blank=True, null=True
    )  # Sales transaction date
    hipoteca = models.BooleanField(default=False)  # Mortgage
    monto = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Amount
    tasa_efectiva = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Effective rate
    tasa_nominal = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Nominal rate
    interes_anual = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Annual interest
    feci = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # FECI
    interes_anual_feci = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Annual interest + FECI
    nombre = models.TextField(blank=True, null=True)  # Name
    filing_date = models.DateField(blank=True, null=True)  # Filing date

    class Meta:
        db_table = "PDF_Raw_Data"
        # unique_together = (("folio", "edificio"),)
        verbose_name_plural = "PDF Raw Data"

    def get_s3_file_path(self):
        if self.building and self.folio and self.filename:
            print(self.filename, 'File___Name')
            encoded_filename = quote(self.filename)
            # encoded_filename = urllib.parse.quote(self.filename, safe='/-_.,()=')
            # encoded_filename = encoded_filename.replace(',', '%2C')
            print(encoded_filename, 'encoded_filename')
            
            # print(encoded_filename, 'encoded_filename')
            # encoded_filename = normalize_s3_key(self.filename)
            # print(encoded_filename, 'encoded_filename')
            # if "Asiento" in encoded_filename:  # Just an example condition for files that need double encoding
            #     encoded_filename = encoded_filename.replace('%', '%25')

            return f'{self.building.guid}/Folio_PDFs/{self.folio.folio}/{encoded_filename}'
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


import unicodedata
def normalize_s3_key(file_path):
    """
    Normalizes and encodes a file path for S3 storage to handle special characters correctly.
    """
    # First, normalize unicode characters to their composed form (NFC)
    normalized = unicodedata.normalize('NFC', file_path)
    # normalized = normalized.replace('é', '%CC%81')  # Replace 'é' with '%CC%81'
    # normalized = normalized.replace('í', '%CC%81')  # Similarly, replace other accented characters if needed
    # normalized = normalized.replace('ó', '%CC%81')
    # URL encode the path, but handle structural characters correctly
    # We need to preserve commas as well as parentheses
    # encoded = urllib.parse.quote(normalized, safe='/-_.,()=')  
    encoded = quote(normalized)  
    # Fix any potential double-encoding
    # encoded = encoded.replace('%25', '%')
    # encoded = encoded.replace('é', '%CC%81')
    # encoded = encoded.replace('í', '%CC%81')
    # encoded = encoded.replace('ó', '%CC%81')

    
    # encoded = encoded.replace('%', '%25')
    return encoded

class FoliosHistory(models.Model):
    folio = models.ForeignKey(Folios, on_delete=models.CASCADE) 
    history_id = models.AutoField(primary_key=True) #r
    modulo = models.TextField(null=True, blank=True) 
    codigo_ubicacion = models.IntegerField(null=True, blank=True) 
    municipio = models.TextField(null=True, blank=True)
    edificio = models.TextField()
    propietarios = models.TextField(null=True, blank=True)
    folio_finca_ficha = models.TextField(null=True, blank=True)
    fecha_de_inscripcion = models.DateField(null=True, blank=True)
    propietario = models.TextField(null=True, blank=True)
    domicilio = models.TextField(null=True, blank=True)
    uso_del_suelo = models.TextField(null=True, blank=True)
    otro_tipo = models.TextField(null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    por_edificio = models.TextField(null=True, blank=True)
    porcentaje_de_proindiviso = models.TextField(null=True, blank=True)
    cedula_catastral = models.TextField(null=True, blank=True)
    valor = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    valor_del_terreno = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    valor_de_mejoras = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    valor_del_traspaso = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    numero_de_plano = models.TextField(null=True, blank=True)
    fecha_de_construccion = models.DateField(null=True, blank=True)
    fecha_de_ocupacion = models.DateField(null=True, blank=True)
    lote = models.TextField(null=True, blank=True)
    superficie_inicial = models.TextField(null=True, blank=True)
    superficie_resto_libre = models.TextField(null=True, blank=True)
    colindancias = models.TextField(null=True, blank=True)
    timestamp_added_to_csv = models.DateTimeField(null=True, blank=True)
    derechos_actos_otras_operaciones = models.TextField(null=True, blank=True)
    change_timestamp = models.DateTimeField(auto_now_add=True) #r

    class Meta:
        db_table = "FoliosHistory"
        verbose_name_plural = "Folios History"



class MetricsHistory(models.Model):
    metric = models.ForeignKey(Metrics, on_delete=models.CASCADE)  # folio
    codigo_ubicacion = models.IntegerField(blank=True, null=True)  # Location code
    municipio = models.TextField(blank=True, null=True)  # Municipality
    edificio = models.TextField()  # Building
    fecha_de_construccion = models.DateField(blank=True, null=True)  # Construction date
    fecha_de_ocupacion = models.DateField(blank=True, null=True)  # Occupation date
    propietarios = models.TextField(blank=True, null=True)  # Owners
    domicilio = models.TextField(blank=True, null=True)  # Address
    sales_transaction_date = models.DateField(
        blank=True, null=True
    )  # Sales Transaction Date
    valor = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Value
    valor_del_terreno = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Land value
    valor_de_mejoras = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Improvement value
    valor_del_traspaso = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Transfer value  / Sales Amount
    superficie_inicial = models.TextField(
        blank=True, null=True
    )  # Initial area / square meter
    price_per_square_meter = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Price per square meter
    hipoteca = models.BooleanField(blank=True, null=True)  # Mortgage
    monto = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Amount /Sales Amount
    tasa_efectiva = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Effective rate
    tasa_nominal = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Nominal rate
    interes_anual = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Annual interest
    feci = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # FECI
    interes_anual_feci = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Annual interest + FECI
    nombre = models.TextField(blank=True, null=True)  # Name / Lending Entity
    timestamp = models.DateTimeField(blank=True, null=True)  # Timestamp /Date Added
    uso_del_suelo = models.TextField(blank=True, null=True)  # Land use

    class Meta:
        db_table = "Metrics_History"
        # unique_together = (("metric", "edificio"),)
        verbose_name_plural = "Metrics History"

    def __str__(self):
        return str(self.metric.folio)




class PDFRawDataHistory(models.Model):
    pdf_data = models.ForeignKey(PDFRawData, on_delete=models.CASCADE)  # Folio
    edificio = models.TextField()  # Building
    filename = models.TextField(blank=True, null=True)  # Filename
    pdf_text = models.TextField(blank=True, null=True)  # pdf text
    valor_del_terreno = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Land value
    valor_de_mejoras = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Improvement value
    valor_del_traspaso = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Transfer value
    superficie_inicial = models.TextField(blank=True, null=True)  # Initial area
    sales_transaction_date = models.DateField(
        blank=True, null=True
    )  # Sales transaction date
    hipoteca = models.BooleanField(default=False)  # Mortgage
    monto = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Amount
    tasa_efectiva = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Effective rate
    tasa_nominal = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Nominal rate
    interes_anual = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Annual interest
    feci = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # FECI
    interes_anual_feci = models.DecimalField(
        max_digits=19, decimal_places=2, blank=True, null=True
    )  # Annual interest + FECI
    nombre = models.TextField(blank=True, null=True)  # Name
    filing_date = models.DateField(blank=True, null=True)  # Filing date

    class Meta:
        db_table = "PDF_Raw_Data_History"
        # unique_together = (("folio", "edificio"),)
        verbose_name_plural = "PDF Raw Data History"