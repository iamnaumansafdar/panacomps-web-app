import csv
from django.contrib import admin
from django import forms
from .models import Folios, BarriosEdificios

from django.urls import path
from django.shortcuts import redirect, render
from datetime import datetime
from .models import *
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .forms import FolioMassUpdateForm, MetricMassUpdateForm, PDFDataMassUpdateForm
from .utils import parse_integer, parse_datetime

class CsvImportForm(forms.Form):
    building = forms.ModelChoiceField(queryset=Building.objects.all().order_by('name'), required=True, label="Select Building")
    csv_file = forms.FileField()
   


class FoliosHistoryInline(admin.TabularInline):
    model = FoliosHistory
    extra = 0
    readonly_fields = [field.name for field in FoliosHistory._meta.fields if field.name != 'id']
    

@admin.action(description='Folio Mass update selected records')
def mass_update_folios(modeladmin, request, queryset):
    # Handle the form submission
    print(request.POST)
    if request.method == 'POST' and 'confirm' in request.POST:
        form = FolioMassUpdateForm(request.POST)
        if form.is_valid():
            field = form.cleaned_data['field']
            value = form.cleaned_data['value']
            queryset.update(**{field: value})
            modeladmin.message_user(request, f"Successfully updated {queryset.count()} records.")
            return redirect(request.get_full_path())  # Redirect to avoid resubmission
        else:
            modeladmin.message_user(request, "There was an error with the form submission.", level="error")
    else:
        # Render the form
        form = FolioMassUpdateForm()

    return render(request, 'admin/folio_mass_update.html', {
        'form': form,
        'queryset': queryset,
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
    })

@admin.register(Folios)
class FoliosAdmin(admin.ModelAdmin):
    list_display = ('folio', 'edificio', 'fecha_de_inscripcion', 'valor', 'timestamp_added_to_csv')
    actions = [mass_update_folios]
    search_fields = ('folio', 'edificio', 'propietario', 'codigo_ubicacion', 'municipio')
    list_filter = ('codigo_ubicacion', 'municipio', 'fecha_de_inscripcion')
    readonly_fields = ('timestamp_added_to_csv',)
    inlines = [FoliosHistoryInline]

    change_list_template = "admin/folios_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                selected_building = form.cleaned_data['building']
                try:
                    # Ensure the file is opened in text mode ('r')
                    csv_data = csv_file.read().decode('utf-8').splitlines()
                    reader = csv.reader(csv_data)
                    next(reader)  # Skip header row
                    all_exist = True
                    sql_logs = []
                    for row in reader:
                        # Extract data from CSV row
                        folio, modulo, codigo_ubicacion, municipio, edificio, propietarios, \
                        folio_finca_ficha, fecha_de_inscripcion_str, propietario, domicilio, \
                        uso_del_suelo, otro_tipo, descripcion, por_edificio, porcentaje_de_proindiviso_str, \
                        cedula_catastral, valor_str, valor_del_terreno_str, valor_de_mejoras_str, \
                        valor_del_traspaso_str, numero_de_plano, fecha_de_construccion_str, fecha_de_ocupacion_str, \
                        lote, superficie_inicial, superficie_resto_libre, colindancias, timestamp_added_to_csv_str, \
                        derechos_actos_otras_operaciones = row

                        # Convert decimal fields from string to Decimal format, handle empty strings
                        try:
                            porcentaje_de_proindiviso = float(porcentaje_de_proindiviso_str) if porcentaje_de_proindiviso_str else None
                        except ValueError:
                            porcentaje_de_proindiviso = None

                        try:
                            valor = float(valor_str) if valor_str else None
                        except ValueError:
                            valor = None

                        try:
                            valor_del_terreno = float(valor_del_terreno_str) if valor_del_terreno_str else None
                        except ValueError:
                            valor_del_terreno = None

                        try:
                            valor_de_mejoras = float(valor_de_mejoras_str) if valor_de_mejoras_str else None
                        except ValueError:
                            valor_de_mejoras = None

                        try:
                            valor_del_traspaso = float(valor_del_traspaso_str) if valor_del_traspaso_str else None
                        except ValueError:
                            valor_del_traspaso = None

                        # Convert dates from string to datetime format, handle empty strings
                        fecha_de_inscripcion = datetime.strptime(fecha_de_inscripcion_str, '%d/%m/%Y').date() if fecha_de_inscripcion_str else None
                        fecha_de_construccion = datetime.strptime(fecha_de_construccion_str, '%d/%m/%Y').date() if fecha_de_construccion_str else None
                        fecha_de_ocupacion = datetime.strptime(fecha_de_ocupacion_str, '%d/%m/%Y').date() if fecha_de_ocupacion_str else None

                        # Convert timestamp string to datetime format
                        if timestamp_added_to_csv_str:
                            timestamp_added_to_csv = datetime.strptime(timestamp_added_to_csv_str, '%Y-%m-%d %H:%M:%S %Z')
                        else:
                            timestamp_added_to_csv = None

                        # folio_obj = Folios.objects.get(folio=folio)
                        

                        try:
                            folio_obj = Folios.objects.get(folio=folio)
                            # Create a history entry
                            FoliosHistory.objects.create(
                                folio=folio_obj,
                                modulo=folio_obj.modulo,
                                codigo_ubicacion=folio_obj.codigo_ubicacion,
                                municipio=folio_obj.municipio,
                                edificio=folio_obj.edificio,
                                propietarios=folio_obj.propietarios,
                                folio_finca_ficha=folio_obj.folio_finca_ficha,
                                fecha_de_inscripcion=folio_obj.fecha_de_inscripcion,
                                propietario=folio_obj.propietario,
                                domicilio=folio_obj.domicilio,
                                uso_del_suelo=folio_obj.uso_del_suelo,
                                otro_tipo=folio_obj.otro_tipo,
                                descripcion=folio_obj.descripcion,
                                por_edificio=folio_obj.por_edificio,
                                porcentaje_de_proindiviso=folio_obj.porcentaje_de_proindiviso,
                                cedula_catastral=folio_obj.cedula_catastral,
                                valor=folio_obj.valor,
                                valor_del_terreno=folio_obj.valor_del_terreno,
                                valor_de_mejoras=folio_obj.valor_de_mejoras,
                                valor_del_traspaso=folio_obj.valor_del_traspaso,
                                numero_de_plano=folio_obj.numero_de_plano,
                                fecha_de_construccion=folio_obj.fecha_de_construccion,
                                fecha_de_ocupacion=folio_obj.fecha_de_ocupacion,
                                lote=folio_obj.lote,
                                superficie_inicial=folio_obj.superficie_inicial,
                                superficie_resto_libre=folio_obj.superficie_resto_libre,
                                colindancias=folio_obj.colindancias,
                                timestamp_added_to_csv=folio_obj.timestamp_added_to_csv,
                                derechos_actos_otras_operaciones=folio_obj.derechos_actos_otras_operaciones,
                            )
                            # Update the existing object with new data
                            folio_obj.modulo = modulo
                            folio_obj.codigo_ubicacion = codigo_ubicacion
                            folio_obj.municipio = municipio
                            folio_obj.edificio = edificio
                            folio_obj.propietarios = propietarios
                            folio_obj.folio_finca_ficha = folio_finca_ficha
                            folio_obj.fecha_de_inscripcion = fecha_de_inscripcion
                            folio_obj.propietario = propietario
                            folio_obj.domicilio = domicilio
                            folio_obj.uso_del_suelo = uso_del_suelo
                            folio_obj.otro_tipo = otro_tipo
                            folio_obj.descripcion = descripcion
                            folio_obj.por_edificio = por_edificio
                            folio_obj.porcentaje_de_proindiviso = porcentaje_de_proindiviso
                            folio_obj.cedula_catastral = cedula_catastral
                            folio_obj.valor = valor
                            folio_obj.valor_del_terreno = valor_del_terreno
                            folio_obj.valor_de_mejoras = valor_de_mejoras
                            folio_obj.valor_del_traspaso = valor_del_traspaso
                            folio_obj.numero_de_plano = numero_de_plano
                            folio_obj.fecha_de_construccion = fecha_de_construccion
                            folio_obj.fecha_de_ocupacion = fecha_de_ocupacion
                            folio_obj.lote = lote
                            folio_obj.superficie_inicial = superficie_inicial
                            folio_obj.superficie_resto_libre = superficie_resto_libre
                            folio_obj.colindancias = colindancias
                            folio_obj.timestamp_added_to_csv = timestamp_added_to_csv
                            folio_obj.derechos_actos_otras_operaciones = derechos_actos_otras_operaciones
                            folio_obj.building = selected_building 

                            folio_obj.save()
                            # sql_logs.append(f"UPDATE Folios SET ... WHERE folio={folio};")  # Example log
                            
                        except Folios.DoesNotExist:
                            all_exist = False
                            # Create Folios object
                            Folios.objects.create(
                                folio=folio,
                                modulo=modulo,
                                codigo_ubicacion=codigo_ubicacion,
                                municipio=municipio,
                                edificio=edificio,
                                propietarios=propietarios,
                                folio_finca_ficha=folio_finca_ficha,
                                fecha_de_inscripcion=fecha_de_inscripcion,
                                propietario=propietario,
                                domicilio=domicilio,
                                uso_del_suelo=uso_del_suelo,
                                otro_tipo=otro_tipo,
                                descripcion=descripcion,
                                por_edificio=por_edificio,
                                porcentaje_de_proindiviso=porcentaje_de_proindiviso,
                                cedula_catastral=cedula_catastral,
                                valor=valor,
                                valor_del_terreno=valor_del_terreno,
                                valor_de_mejoras=valor_de_mejoras,
                                valor_del_traspaso=valor_del_traspaso,
                                numero_de_plano=numero_de_plano,
                                fecha_de_construccion=fecha_de_construccion,
                                fecha_de_ocupacion=fecha_de_ocupacion,
                                lote=lote,
                                superficie_inicial=superficie_inicial,
                                superficie_resto_libre=superficie_resto_libre,
                                colindancias=colindancias,
                                timestamp_added_to_csv=timestamp_added_to_csv,
                                derechos_actos_otras_operaciones=derechos_actos_otras_operaciones,
                                building=selected_building
                            )
                            # sql_logs.append(f"INSERT INTO Folios (...) VALUES (...);")

                    if all_exist:
                      self.message_user(request, "Data added to the Folios history table and the existing Folios Table is updated successfully.")
                    else:
                        self.message_user(request, "CSV file imported successfully.")
                    # self.message_user(request, "CSV file imported successfully.")
                    # return render(request, "admin/csv_import_result.html", {
                    #     'sql_logs': sql_logs,
                    #     'error_logs': None,
                    #     'form': form,
                    # })
                    return redirect("..")  # Redirect back to the changelist view
                except Exception as e:
                    # self.message_user(request, f"Error importing CSV file: {e}")
                    # return redirect("..")  # Redirect back to the changelist view
                    error_logs = str(e)
                    messages.error(request, f"Error importing CSV file: {e}")
                    return render(request, "admin/csv_import_result.html", {
                        'sql_logs': sql_logs,
                        'error_logs': error_logs,
                        'form': form,
                    })
        else:
            form = CsvImportForm()

        payload = {
            "form": form,
            "title": "Import Folios.csv CSV File" 
            }
        return render(request, "admin/csv_form.html", payload)


@admin.register(FoliosHistory)
class FoliosHistoryAdmin(admin.ModelAdmin):
    list_display = ('folio', 'edificio', 'fecha_de_inscripcion', 'valor', 'timestamp_added_to_csv')
    search_fields = ('edificio', 'propietario', 'codigo_ubicacion', 'municipio')
    list_filter = ('codigo_ubicacion', 'municipio', 'fecha_de_inscripcion')
    readonly_fields = ('timestamp_added_to_csv',)



class MetricsHistoryInline(admin.TabularInline):
    model = MetricsHistory
    extra = 0
    readonly_fields = [field.name for field in MetricsHistory._meta.fields if field.name != 'id']
    

@admin.action(description='Metric Mass update selected records')
def mass_update_metrics(modeladmin, request, queryset):
    # Handle the form submission
    print(request.POST)
    if request.method == 'POST' and 'confirm' in request.POST:
        print(request.POST, 'POST')
        form = MetricMassUpdateForm(request.POST)
        if form.is_valid():
            field = form.cleaned_data['field']
            value = form.cleaned_data['value']
            queryset.update(**{field: value})
            modeladmin.message_user(request, f"Successfully updated {queryset.count()} records.")
            return redirect(request.get_full_path())  # Redirect to avoid resubmission
        else:
            modeladmin.message_user(request, "There was an error with the form submission.", level="error")
    else:
        # Render the form
        print("here")
        form = MetricMassUpdateForm()

    return render(request, 'admin/metric_mass_update.html', {
        'form': form,
        'queryset': queryset,
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
    })

import logging
logger = logging.getLogger(__name__)
# upload the metric csv
@admin.register(Metrics)
class MetricsAdmin(admin.ModelAdmin):
    list_display = ('folio', 'edificio', 'fecha_de_construccion', 'fecha_de_ocupacion', 'valor', 'timestamp')
    actions = [mass_update_metrics]
    search_fields = ('folio__folio', 'edificio', 'nombre', 'codigo_ubicacion', 'municipio')
    list_filter = ('codigo_ubicacion', 'municipio', 'fecha_de_construccion', 'fecha_de_ocupacion')
    readonly_fields = ('timestamp',)
    inlines = [MetricsHistoryInline]
   

    change_list_template = "admin/metrics_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-metric-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                selected_building = form.cleaned_data['building']
                try:
                    # Ensure the file is opened in text mode ('r')
                    csv_data = csv_file.read().decode('utf-8').splitlines()
                    reader = csv.reader(csv_data)
                    next(reader)  # Skip header row
                    all_exist = True
                    sql_logs = []
                    for row in reader:
                        # Extract data from CSV row
                        folio_id, codigo_ubicacion, municipio, edificio, \
                        fecha_de_construccion_str, fecha_de_ocupacion_str, propietarios, \
                        domicilio, sales_transaction_date_str, valor_str, valor_del_terreno_str, \
                        valor_de_mejoras_str, valor_del_traspaso_str, superficie_inicial, \
                        price_per_square_meter_str, hipoteca_str, monto_str, tasa_efectiva_str, \
                        tasa_nominal_str, interes_anual_str, feci_str, interes_anual_feci_str, \
                        nombre, timestamp_str, uso_del_suelo = row


                        # Convert date fields
                        try:
                            fecha_de_construccion = datetime.strptime(fecha_de_construccion_str, '%d/%m/%Y').date() if fecha_de_construccion_str else None
                        except ValueError:
                            fecha_de_construccion = None

                        try:
                            fecha_de_ocupacion = datetime.strptime(fecha_de_ocupacion_str, '%d/%m/%Y').date() if fecha_de_ocupacion_str else None
                        except ValueError:
                            fecha_de_ocupacion = None

                        try:
                            sales_transaction_date = datetime.strptime(sales_transaction_date_str, '%d/%m/%Y').date() if sales_transaction_date_str else None
                        except ValueError:
                            sales_transaction_date = None

                        # Convert decimal fields
                        try:
                            valor = float(valor_str) if valor_str else None
                        except ValueError:
                            valor = None

                        try:
                            valor_del_terreno = float(valor_del_terreno_str) if valor_del_terreno_str else None
                        except ValueError:
                            valor_del_terreno = None

                        try:
                            valor_de_mejoras = float(valor_de_mejoras_str) if valor_de_mejoras_str else None
                        except ValueError:
                            valor_de_mejoras = None

                        try:
                            valor_del_traspaso = float(valor_del_traspaso_str) if valor_del_traspaso_str else None
                        except ValueError:
                            valor_del_traspaso = None

                        try:
                            price_per_square_meter = float(price_per_square_meter_str) if price_per_square_meter_str else None
                        except ValueError:
                            price_per_square_meter = None

                        # Convert boolean field
                        hipoteca_str_cleaned = hipoteca_str.strip().lower()
                        hipoteca = True if hipoteca_str_cleaned == 'yes' else False if hipoteca_str_cleaned == 'no' else None

                        # Convert decimal fields for monetary values
                        try:
                            monto = float(monto_str) if monto_str else None
                        except ValueError:
                            monto = None

                        try:
                            tasa_efectiva = float(tasa_efectiva_str) if tasa_efectiva_str else None
                        except ValueError:
                            tasa_efectiva = None

                        try:
                            tasa_nominal = float(tasa_nominal_str) if tasa_nominal_str else None
                        except ValueError:
                            tasa_nominal = None

                        try:
                            interes_anual = float(interes_anual_str) if interes_anual_str else None
                        except ValueError:
                            interes_anual = None

                        try:
                            feci = float(feci_str) if feci_str else None
                        except ValueError:
                            feci = None

                        try:
                            interes_anual_feci = float(interes_anual_feci_str) if interes_anual_feci_str else None
                        except ValueError:
                            interes_anual_feci = None

                        # Convert timestamp string to datetime format
                        try:
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S %Z')
                        except ValueError:
                            timestamp = None

                        # Find corresponding Folios object
                        try:
                            folio = Folios.objects.get(folio=folio_id)
                            print(folio, 'F')
                        except Folios.DoesNotExist:
                            # messages.error(request, f"Folio with ID {folio_id} does not exist.")
                            error_logs = str(folio_id)
                            # self.message_user(request, f"Folio with ID {folio_id} does not exist.")
                            messages.error(request, f"Folio with ID {folio_id} does not exist.")
                            # return redirect("..")
                            return render(request, "admin/csv_import_result.html", {
                                'sql_logs': sql_logs,
                                'error_logs': error_logs,
                                'form': form,
                            })
                        
                        # metric_obj, created = Metrics.objects.get_or_create(folio=folio)
                        try:
                            metric_obj = Metrics.objects.get(folio=folio)
                            # Update the existing Metrics object with new data

                            MetricsHistory.objects.create(
                                metric=metric_obj,
                                codigo_ubicacion=metric_obj.codigo_ubicacion,
                                municipio=metric_obj.municipio,
                                edificio=metric_obj.edificio,
                                fecha_de_construccion=metric_obj.fecha_de_construccion,
                                fecha_de_ocupacion=metric_obj.fecha_de_ocupacion,
                                propietarios=metric_obj.propietarios,
                                domicilio=metric_obj.domicilio,
                                sales_transaction_date=metric_obj.sales_transaction_date,
                                valor=metric_obj.valor,
                                valor_del_terreno=metric_obj.valor_del_terreno,
                                valor_de_mejoras=metric_obj.valor_de_mejoras,
                                valor_del_traspaso=metric_obj.valor_del_traspaso,
                                superficie_inicial=metric_obj.superficie_inicial,
                                price_per_square_meter=metric_obj.price_per_square_meter,
                                hipoteca=metric_obj.hipoteca,
                                monto=metric_obj.monto,
                                tasa_efectiva=metric_obj.tasa_efectiva,
                                tasa_nominal=metric_obj.tasa_nominal,
                                interes_anual=metric_obj.interes_anual,
                                feci=metric_obj.feci,
                                interes_anual_feci=metric_obj.interes_anual_feci,
                                nombre=metric_obj.nombre,
                                timestamp=metric_obj.timestamp,
                                uso_del_suelo=metric_obj.uso_del_suelo,
                            )


                            metric_obj.codigo_ubicacion = codigo_ubicacion
                            metric_obj.municipio = municipio
                            metric_obj.edificio = edificio
                            metric_obj.fecha_de_construccion = fecha_de_construccion
                            metric_obj.fecha_de_ocupacion = fecha_de_ocupacion
                            metric_obj.propietarios = propietarios
                            metric_obj.domicilio = domicilio
                            metric_obj.sales_transaction_date = sales_transaction_date
                            metric_obj.valor = valor
                            metric_obj.valor_del_terreno = valor_del_terreno
                            metric_obj.valor_de_mejoras = valor_de_mejoras
                            metric_obj.valor_del_traspaso = valor_del_traspaso
                            metric_obj.superficie_inicial = superficie_inicial
                            metric_obj.price_per_square_meter = price_per_square_meter
                            metric_obj.hipoteca = hipoteca
                            metric_obj.monto = monto
                            metric_obj.tasa_efectiva = tasa_efectiva
                            metric_obj.tasa_nominal = tasa_nominal
                            metric_obj.interes_anual = interes_anual
                            metric_obj.feci = feci
                            metric_obj.interes_anual_feci = interes_anual_feci
                            metric_obj.nombre = nombre
                            metric_obj.timestamp = timestamp
                            metric_obj.uso_del_suelo = uso_del_suelo
                            metric_obj.building = selected_building

                            metric_obj.save()
                            sql_logs.append(f"UPDATE Folios SET ... WHERE folio={folio};")  # Example log


                        except Metrics.DoesNotExist:
                            all_exist = False

                            # Create Metrics object
                            Metrics.objects.create(
                                folio=folio,
                                codigo_ubicacion=codigo_ubicacion,
                                municipio=municipio,
                                edificio=edificio,
                                fecha_de_construccion=fecha_de_construccion,
                                fecha_de_ocupacion=fecha_de_ocupacion,
                                propietarios=propietarios,
                                domicilio=domicilio,
                                sales_transaction_date=sales_transaction_date,
                                valor=valor,
                                valor_del_terreno=valor_del_terreno,
                                valor_de_mejoras=valor_de_mejoras,
                                valor_del_traspaso=valor_del_traspaso,
                                superficie_inicial=superficie_inicial,
                                price_per_square_meter=price_per_square_meter,
                                hipoteca=hipoteca,
                                monto=monto,
                                tasa_efectiva=tasa_efectiva,
                                tasa_nominal=tasa_nominal,
                                interes_anual=interes_anual,
                                feci=feci,
                                interes_anual_feci=interes_anual_feci,
                                nombre=nombre,
                                timestamp=timestamp,
                                uso_del_suelo=uso_del_suelo,
                                building=selected_building
                            )
                            sql_logs.append(f"INSERT INTO Folios (...) VALUES (...);")

                    
                    if all_exist:
                      self.message_user(request, "Data added to the Metrics history table and the existing Metrics Table is updated successfully.")
                    else:
                        self.message_user(request, "CSV file imported successfully.")
                    return redirect("..")  # Redirect back to the changelist view

                except Exception as e:
                    # self.message_user(request, f"Error importing CSV file: {e}")
                    # return redirect("..")  # Redirect back to the changelist view
                    error_logs = str(e)
                    messages.error(request, f"Error importing CSV file: {e}")
                    return render(request, "admin/csv_import_result.html", {
                        'sql_logs': sql_logs,
                        'error_logs': error_logs,
                        'form': form,
                    })

        else:
            form = CsvImportForm()

        payload = {
            "form": form,
            "title": "Import Metrics.csv CSV File" 
            }
        return render(request, "admin/csv_form.html", payload)


@admin.register(MetricsHistory)
class MetricsHistoryAdmin(admin.ModelAdmin):
    list_display = ('metric', 'edificio', 'fecha_de_construccion', 'fecha_de_ocupacion', 'valor', 'timestamp')
    search_fields = ('metric__folio__folio', 'edificio', 'nombre', 'codigo_ubicacion', 'municipio')
    list_filter = ('codigo_ubicacion', 'municipio', 'fecha_de_construccion', 'fecha_de_ocupacion')
    readonly_fields = ('timestamp',)


class PDFRawDataHistoryInline(admin.TabularInline):
    model = PDFRawDataHistory
    extra = 0
    readonly_fields = [field.name for field in PDFRawDataHistory._meta.fields if field.name != 'id']


@admin.action(description='PDFData Mass update selected records')
def mass_update_pdfdata(modeladmin, request, queryset):
    # Handle the form submission
    print(request.POST)
    if request.method == 'POST' and 'confirm' in request.POST:
        form = PDFDataMassUpdateForm(request.POST)
        if form.is_valid():
            field = form.cleaned_data['field']
            value = form.cleaned_data['value']
            queryset.update(**{field: value})
            modeladmin.message_user(request, f"Successfully updated {queryset.count()} records.")
            return redirect(request.get_full_path())  # Redirect to avoid resubmission
        else:
            modeladmin.message_user(request, "There was an error with the form submission.", level="error")
    else:
        # Render the form
        form = PDFDataMassUpdateForm()

    return render(request, 'admin/pdf_mass_update.html', {
        'form': form,
        'queryset': queryset,
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
    })


# Upload CSV for pdfrawdata
@admin.register(PDFRawData)
class PDFRawDataAdmin(admin.ModelAdmin):
    list_display = ('folio', 'edificio', 'filename', 'sales_transaction_date', 'hipoteca')
    actions = [mass_update_pdfdata]
    search_fields = ('folio__folio', 'edificio', 'filename', 'monto')
    list_filter = ('hipoteca', 'sales_transaction_date')
    inlines = [PDFRawDataHistoryInline]

    change_list_template = "admin/pdfrawdata_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-pdfrawdata-csv/', self.import_csv, name='import-pdfrawdata-csv'),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            # csv_file = request.FILES["csv_file"]
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                selected_building = form.cleaned_data['building']
            try:
                # Ensure the file is opened in text mode ('r')
                csv_data = csv_file.read().decode('utf-8').splitlines()
                reader = csv.reader(csv_data)
                next(reader) 
                sql_logs = []

                all_exist = True  # Flag to track if all data are duplicates

                for row in reader:
                    # Extract data from CSV row
                    folio_id, edificio, filename, pdf_text, valor_del_terreno_str, \
                    valor_de_mejoras_str, valor_del_traspaso_str, superficie_inicial, \
                    sales_transaction_date_str, hipoteca_str, monto_str, tasa_efectiva_str, \
                    tasa_nominal_str, interes_anual_str, feci_str, interes_anual_feci_str, \
                    nombre, filing_date_str = row

                    # Convert date fields
                    try:
                        sales_transaction_date = datetime.strptime(sales_transaction_date_str, '%d/%m/%Y').date() if sales_transaction_date_str else None
                    except ValueError:
                        sales_transaction_date = None

                    try:
                        filing_date = datetime.strptime(filing_date_str, '%d/%m/%Y').date() if filing_date_str else None
                    except ValueError:
                        filing_date = None

                    # Convert decimal fields
                    try:
                        valor_del_terreno = float(valor_del_terreno_str) if valor_del_terreno_str else None
                    except ValueError:
                        valor_del_terreno = None

                    try:
                        valor_de_mejoras = float(valor_de_mejoras_str) if valor_de_mejoras_str else None
                    except ValueError:
                        valor_de_mejoras = None

                    try:
                        valor_del_traspaso = float(valor_del_traspaso_str) if valor_del_traspaso_str else None
                    except ValueError:
                        valor_del_traspaso = None

                    # Find corresponding Folios object
                    try:
                        folio = Folios.objects.get(folio=folio_id)
                    except Folios.DoesNotExist:
                        # self.message_user(request, f"Folio with ID {folio_id} does not exist.")
                        error_logs = str(folio_id)
                        messages.error(request, f"Folio with ID {folio_id} does not exist.")
                        all_exist = False
                        continue

                    existing_pdf = PDFRawData.objects.filter(folio=folio, filename=filename, pdf_text=pdf_text).first()
                    if existing_pdf:
                        # Move existing data to PDFRawDataHistory
                        PDFRawDataHistory.objects.create(
                            pdf_data=existing_pdf,
                            edificio=existing_pdf.edificio,
                            filename=existing_pdf.filename,
                            pdf_text=existing_pdf.pdf_text,
                            valor_del_terreno=existing_pdf.valor_del_terreno,
                            valor_de_mejoras=existing_pdf.valor_de_mejoras,
                            valor_del_traspaso=existing_pdf.valor_del_traspaso,
                            superficie_inicial=existing_pdf.superficie_inicial,
                            sales_transaction_date=existing_pdf.sales_transaction_date,
                            hipoteca=existing_pdf.hipoteca,
                            monto=existing_pdf.monto,
                            tasa_efectiva=existing_pdf.tasa_efectiva,
                            tasa_nominal=existing_pdf.tasa_nominal,
                            interes_anual=existing_pdf.interes_anual,
                            feci=existing_pdf.feci,
                            interes_anual_feci=existing_pdf.interes_anual_feci,
                            nombre=existing_pdf.nombre,
                            filing_date=existing_pdf.filing_date
                        )
                        # Update existing data
                        existing_pdf.edificio = edificio
                        existing_pdf.pdf_text = pdf_text
                        existing_pdf.valor_del_terreno = valor_del_terreno
                        existing_pdf.valor_de_mejoras = valor_de_mejoras
                        existing_pdf.valor_del_traspaso = valor_del_traspaso
                        existing_pdf.superficie_inicial = superficie_inicial
                        existing_pdf.sales_transaction_date = sales_transaction_date
                        existing_pdf.hipoteca = bool(hipoteca_str)
                        existing_pdf.monto = float(monto_str) if monto_str else None
                        existing_pdf.tasa_efectiva = float(tasa_efectiva_str) if tasa_efectiva_str else None
                        existing_pdf.tasa_nominal = float(tasa_nominal_str) if tasa_nominal_str else None
                        existing_pdf.interes_anual = float(interes_anual_str) if interes_anual_str else None
                        existing_pdf.feci = float(feci_str) if feci_str else None
                        existing_pdf.interes_anual_feci = float(interes_anual_feci_str) if interes_anual_feci_str else None
                        existing_pdf.nombre = nombre
                        existing_pdf.filing_date = filing_date
                        existing_pdf.building = selected_building
                        existing_pdf.save()
                        all_exist = True
                        sql_logs.append(f"UPDATE Folios SET ... WHERE folio={folio};")  # Example log
                    else:
                        # Create new PDFRawData object
                        PDFRawData.objects.create(
                            folio=folio,
                            edificio=edificio,
                            filename=filename,
                            pdf_text=pdf_text,
                            valor_del_terreno=valor_del_terreno,
                            valor_de_mejoras=valor_de_mejoras,
                            valor_del_traspaso=valor_del_traspaso,
                            superficie_inicial=superficie_inicial,
                            sales_transaction_date=sales_transaction_date,
                            hipoteca=bool(hipoteca_str),
                            monto=float(monto_str) if monto_str else None,
                            tasa_efectiva=float(tasa_efectiva_str) if tasa_efectiva_str else None,
                            tasa_nominal=float(tasa_nominal_str) if tasa_nominal_str else None,
                            interes_anual=float(interes_anual_str) if interes_anual_str else None,
                            feci=float(feci_str) if feci_str else None,
                            interes_anual_feci=float(interes_anual_feci_str) if interes_anual_feci_str else None,
                            nombre=nombre,
                            filing_date=filing_date,
                            building=selected_building,
                        )
                        all_exist = False
                        sql_logs.append(f"INSERT INTO Folios (...) VALUES (...);")
                    
                    # # Check if a PDFRawData object with the same folio, filename, and pdf_text exists
                    # if PDFRawData.objects.filter(folio=folio, filename=filename, pdf_text=pdf_text).exists():
                    #     try:
                    #         existing_pdf = PDFRawData.objects.filter(folio=folio, filename=filename, pdf_text=pdf_text).first()
                    #         PDFRawDataHistory.objects.create(
                    #             pdf_data=existing_pdf,
                    #             edificio=existing_pdf.edificio,
                    #             filename=existing_pdf.filename,
                    #             pdf_text=existing_pdf.pdf_text,
                    #             valor_del_terreno=existing_pdf.valor_del_terreno,
                    #             valor_de_mejoras=existing_pdf.valor_de_mejoras,
                    #             valor_del_traspaso=existing_pdf.valor_del_traspaso,
                    #             superficie_inicial=existing_pdf.superficie_inicial,
                    #             sales_transaction_date=existing_pdf.sales_transaction_date,
                    #             hipoteca=existing_pdf.hipoteca,
                    #             monto=existing_pdf.monto,
                    #             tasa_efectiva=existing_pdf.tasa_efectiva,
                    #             tasa_nominal=existing_pdf.tasa_nominal,
                    #             interes_anual=existing_pdf.interes_anual,
                    #             feci=existing_pdf.feci,
                    #             interes_anual_feci=existing_pdf.interes_anual_feci,
                    #             nombre=existing_pdf.nombre,
                    #             filing_date=existing_pdf.filing_date
                    #         )
                    #         # Update existing data
                    #         existing_pdf.edificio = edificio
                    #         existing_pdf.pdf_text = pdf_text
                    #         existing_pdf.valor_del_terreno = valor_del_terreno
                    #         existing_pdf.valor_de_mejoras = valor_de_mejoras
                    #         existing_pdf.valor_del_traspaso = valor_del_traspaso
                    #         existing_pdf.superficie_inicial = superficie_inicial
                    #         existing_pdf.sales_transaction_date = sales_transaction_date
                    #         existing_pdf.hipoteca = bool(hipoteca_str)
                    #         existing_pdf.monto = float(monto_str) if monto_str else None
                    #         existing_pdf.tasa_efectiva = float(tasa_efectiva_str) if tasa_efectiva_str else None
                    #         existing_pdf.tasa_nominal = float(tasa_nominal_str) if tasa_nominal_str else None
                    #         existing_pdf.interes_anual = float(interes_anual_str) if interes_anual_str else None
                    #         existing_pdf.feci = float(feci_str) if feci_str else None
                    #         existing_pdf.interes_anual_feci = float(interes_anual_feci_str) if interes_anual_feci_str else None
                    #         existing_pdf.nombre = nombre
                    #         existing_pdf.filing_date = filing_date
                    #         existing_pdf.save()
                    #     except PDFRawData.DoesNotExist:
                    #         # Create PDFRawData object
                    #         PDFRawData.objects.create(
                    #             folio=folio,
                    #             edificio=edificio,
                    #             filename=filename,
                    #             pdf_text=pdf_text,
                    #             valor_del_terreno=valor_del_terreno,
                    #             valor_de_mejoras=valor_de_mejoras,
                    #             valor_del_traspaso=valor_del_traspaso,
                    #             superficie_inicial=superficie_inicial,
                    #             sales_transaction_date=sales_transaction_date,
                    #             hipoteca=bool(hipoteca_str),
                    #             monto=float(monto_str) if monto_str else None,
                    #             tasa_efectiva=float(tasa_efectiva_str) if tasa_efectiva_str else None,
                    #             tasa_nominal=float(tasa_nominal_str) if tasa_nominal_str else None,
                    #             interes_anual=float(interes_anual_str) if interes_anual_str else None,
                    #             feci=float(feci_str) if feci_str else None,
                    #             interes_anual_feci=float(interes_anual_feci_str) if interes_anual_feci_str else None,
                    #             nombre=nombre,
                    #             filing_date=filing_date,
                    #         )
                    #         all_exist = False  # Set the flag to False if any new data is created
                    # else:
                    #     # Create PDFRawData object
                    #     PDFRawData.objects.create(
                    #             folio=folio,
                    #             edificio=edificio,
                    #             filename=filename,
                    #             pdf_text=pdf_text,
                    #             valor_del_terreno=valor_del_terreno,
                    #             valor_de_mejoras=valor_de_mejoras,
                    #             valor_del_traspaso=valor_del_traspaso,
                    #             superficie_inicial=superficie_inicial,
                    #             sales_transaction_date=sales_transaction_date,
                    #             hipoteca=bool(hipoteca_str),
                    #             monto=float(monto_str) if monto_str else None,
                    #             tasa_efectiva=float(tasa_efectiva_str) if tasa_efectiva_str else None,
                    #             tasa_nominal=float(tasa_nominal_str) if tasa_nominal_str else None,
                    #             interes_anual=float(interes_anual_str) if interes_anual_str else None,
                    #             feci=float(feci_str) if feci_str else None,
                    #             interes_anual_feci=float(interes_anual_feci_str) if interes_anual_feci_str else None,
                    #             nombre=nombre,
                    #             filing_date=filing_date,
                    #         )
                    #     all_exist = False

                if all_exist:
                    self.message_user(request, "Data added to the PDF Raw Data history table and the existing PDF Raw Data Table is updated successfully.")
                else:
                    self.message_user(request, "CSV file imported successfully.")
                return redirect("..")  

            except Exception as e:
                # self.message_user(request, f"Error importing CSV file: {e}")
                # self.message_user(request, f"Error importing CSV file: {e}")
                error_logs = str(e)
                messages.error(request, f"Error importing CSV file: {e}")
                return render(request, "admin/csv_import_result.html", {
                        'sql_logs': sql_logs,
                        'error_logs': error_logs,
                        'form': form,
                    })

        form = CsvImportForm()
        payload = {
            "form": form,
            "title": "Import PDFRawData.csv CSV File" 
            }
        return render(request, "admin/csv_form.html", payload)


@admin.register(PDFRawDataHistory)
class PDFRawDataHistoryAdmin(admin.ModelAdmin):
    list_display = ('pdf_data', 'edificio', 'filename', 'sales_transaction_date', 'hipoteca')
    search_fields = ('edificio', 'filename', 'monto')
    list_filter = ('hipoteca', 'sales_transaction_date')



# @admin.register(Building)
# class BuildingAdmin(admin.ModelAdmin):
#     list_display = ('guid', 'nombre_barrio', 'name', 'street', 'address_1', 'email')
#     search_fields = ('name', 'guid', 'email')
#     list_filter = ('nombre_barrio', 'name', 'email')


 


from django.db import IntegrityError

class CsvBuildingImportForm(forms.Form):
    # building = forms.ModelChoiceField(queryset=Building.objects.all(), required=True, label="Select Building")
    csv_file = forms.FileField()


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('guid', 'nombre_barrio', 'name', 'street', 'address_1', 'email')
    actions = ['import_building_csv']
    search_fields = ('name', 'guid', 'email')
    list_filter = ('nombre_barrio', 'name', 'email')
   

    change_list_template = "admin/building_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import_building_csv/', self.import_building_csv),
        ]
        return my_urls + urls


    def import_building_csv(self, request):
        if request.method == "POST":
            form = CsvBuildingImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                all_exist = True
                sql_logs = []
                error_logs = []
                try:
                    csv_data = csv_file.read().decode('utf-8').splitlines()
                    reader = csv.reader(csv_data)
                    next(reader)  # Skip header
                    for row in reader:
                        # Unpack CSV values (filling missing columns with None)
                        (guid, nombre_barrio, name, street, address_1, address_2, district_id, city_id, location_id, postcode, 
                        email, telephone_nr, mobile_nr, fax_nr, youtube_id, latitude, longitude, slug, units, stars, rating, 
                        floors_count, construction_year, status, gmaps_place_id, building_type, developer, amenities, 
                        occupancy_permit_date, registry_code, energy_certification, security_features, owner_association, 
                        rentals_allowed, rental_type) = (row + [None] * (35 - len(row)))


                        # Convert date strings to date objects
                        # # Convert time strings to time objects
                        # hora_registro =  TimeUtils.parse_time(hora_registro_str) if hora_registro_str else time(0, 0)

                        # district_id = int(district_id) if district_id else None
                        district_id = parse_integer(district_id)
                        city_id = parse_integer(city_id)
                        location_id = parse_integer(location_id)
                        construction_year = parse_integer(construction_year)
                        postcode = parse_integer(postcode) 
                        latitude = float(latitude) if latitude else None
                        longitude = float(longitude) if longitude else None
                        units = int(units) if units else None
                        stars = float(stars) if stars else None
                        rating = float(rating) if rating else None
                        floors_count = int(floors_count) if floors_count else None
                        # construction_year = int(construction_year) if construction_year else None
                        occupancy_permit_date = parse_datetime(occupancy_permit_date)
                        # occupancy_permit_date = datetime.strptime(occupancy_permit_date, '%d/%m/%Y').date() if occupancy_permit_date else None
                        rentals_allowed = bool(rentals_allowed) if rentals_allowed is not None and rentals_allowed != '' else False



                        if nombre_barrio:
                            barrio_obj = BarriosEdificios.objects.filter(nombre_barrio=nombre_barrio).first()
                            print(barrio_obj, 'barrio_obj')
                            if not barrio_obj:
                                error_message = f"Error: Barrio '{nombre_barrio}' not found. Please create this barrio and retry."
                                error_logs.append(error_message)
                                continue  # Skip to the next row
                        else:
                            error_message = f"Error: Barrio '{nombre_barrio}' not found. Please create this barrio where building '{name} and guid '{guid}' and retry."
                            error_logs.append(error_message)
                            continue  # Skip to the next row

                        # Skip creating buildings with duplicate GUIDs
                        try:
                            Building.objects.create(
                                guid=int(guid),
                                nombre_barrio=barrio_obj,  # ForeignKey to BarriosEdificios
                                name=name,
                                street=street,
                                address_1=address_1,
                                address_2=address_2,
                                district_id=district_id,
                                city_id=city_id,
                                location_id=location_id,
                                postcode=postcode,
                                email=email,
                                telephone_nr=telephone_nr,
                                mobile_nr=mobile_nr,
                                fax_nr=fax_nr,
                                youtube_id=youtube_id,
                                latitude=latitude,
                                longitude=longitude,
                                slug=slug,
                                units=units,
                                stars=stars,
                                rating=rating,
                                floors_count=floors_count,
                                construction_year=construction_year,
                                status=status,
                                gmaps_place_id=gmaps_place_id,
                                building_type=building_type,
                                developer=developer,
                                amenities=amenities,
                                occupancy_permit_date=occupancy_permit_date,
                                registry_code=registry_code,
                                energy_certification=energy_certification,
                                security_features=security_features,
                                owner_association=owner_association,
                                rentals_allowed=rentals_allowed,
                                rental_type=rental_type
                            )
                        except IntegrityError:
                            sql_logs.append(f"Building with GUID {guid} already exists. Skipping this building.")
                            continue  # Skip to the next row

                    # Show error logs if any barrios were missing
                    if error_logs:
                        messages.error(request, "\n".join(error_logs))
                        return render(request, "admin/csv_import_result.html", {
                            'sql_logs': sql_logs,
                            'error_logs': error_logs,
                            'form': form,
                        })

                    # If no errors, confirm success
                    self.message_user(request, "CSV file imported successfully.")
                    return redirect("..")

                except Exception as e:
                    error_logs.append(str(e))
                    messages.error(request, f"Error importing CSV file: {e}")
                    return render(request, "admin/csv_import_result.html", {
                        'sql_logs': sql_logs,
                        'error_logs': error_logs,
                        'form': form,
                    })
        else:
            form = CsvBuildingImportForm()

        return render(request, 'admin/csv_form.html', {'form': form, 'title': 'Import Building CSV File'})


@admin.register(BarriosEdificios)
class BarriosEdificiosAdmin(admin.ModelAdmin):
    list_display = ('guid', 'nombre_barrio',  'descripcion_barrio')
    actions = ['import_barrios_csv']
    search_fields = ('nombre_barrio', 'guid')
    list_filter = ('nombre_barrio', 'guid')
   

    change_list_template = "admin/barrios_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import_barrios_csv/', self.import_barrios_csv),
        ]
        return my_urls + urls


    def import_barrios_csv(self, request):
        if request.method == "POST":
            form = CsvBuildingImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                all_exist = True
                sql_logs = []
                error_logs = []
                try:
                    csv_data = csv_file.read().decode('utf-8').splitlines()
                    reader = csv.reader(csv_data)
                    next(reader)  
                    for row in reader:
                        (guid, NOMBRE_BARRIO, DESCRIPCION_BARRIO) = (row + [None] * (3 - len(row)))

                        if BarriosEdificios.objects.filter(guid=guid).exists():
                            error_logs.append(f"Barrio with GUID {guid} already exists.")
                            continue
                        if BarriosEdificios.objects.filter(nombre_barrio=NOMBRE_BARRIO).exists():
                            error_logs.append(f"Barrio with name {NOMBRE_BARRIO} already exists.")
                            continue

                        try:
                            BarriosEdificios.objects.create(
                                guid=int(guid),
                                nombre_barrio=NOMBRE_BARRIO,  
                                descripcion_barrio=DESCRIPCION_BARRIO)
                        except IntegrityError:
                            # sql_logs.append(f"Barrios with GUID {guid} or {NOMBRE_BARRIO} already exists. Skipping this Barrios.")
                            continue  
                    if error_logs:
                        messages.error(request, "\n".join(error_logs))
                        return render(request, "admin/csv_import_result.html", {
                            'sql_logs': sql_logs,
                            'error_logs': error_logs,
                            'form': form,
                        })
                    
                    self.message_user(request, "CSV file imported successfully.")
                    return redirect("..")

                except Exception as e:
                    error_logs.append(str(e))
                    messages.error(request, f"Error importing CSV file: {e}")
                    return render(request, "admin/csv_import_result.html", {
                        'sql_logs': sql_logs,
                        'error_logs': error_logs,
                        'form': form,
                    })
        else:
            form = CsvBuildingImportForm()

        return render(request, 'admin/csv_form.html', {'form': form, 'title': 'Import Barrios CSV File'})


