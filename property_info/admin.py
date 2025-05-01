import csv
from django.urls import path
from django.contrib import admin
from django import forms
from django.shortcuts import render, redirect
from .models import Gravamen, Remate
from panaEstate.models import Building
from django.contrib import messages
from datetime import datetime
from datetime import datetime, time
from .utils import TimeUtils, CsvUtils

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()
    building = forms.ModelChoiceField(queryset=Building.objects.all().order_by('name'))

@admin.register(Gravamen)
class GravamenAdmin(admin.ModelAdmin):
    list_display = ('folio', 'edificio', 'fecha_oficio', 'num_auto', 'building')
    search_fields = ['folio', 'edificio', 'nombre_organo', 'provincia_organo', 'num_oficio']
    actions = ['import_gravamenes_csv']
    change_list_template = "admin/grava_changelist.html"
    # change_list_template = "admin/csv_import.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-gravamenes-csv/', self.admin_site.admin_view(self.import_gravamenes_csv))
        ]
        return custom_urls + urls

    def import_gravamenes_csv(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                selected_building = form.cleaned_data['building']
                try:
                    rows = CsvUtils.read_csv(csv_file)
                    all_exist = True
                    sql_logs = []
                    for row in rows:

                        folio, edificio, organo_levantamiento, nombre_organo, provincia_organo, \
                        num_oficio, fecha_oficio_str, num_auto, fecha_auto_str, descripcion, \
                        titular_baja_nombre, titular_baja_derecho, fecha_registro_str, hora_registro_str, \
                        num_entrada, doc_presentado_tipo, doc_presentado_fecha_str, nombre_juez, \
                        derechos_registro, nombre_archivo_pdf, contenido_pdf = row
                        # Convert date and time strings to proper types


                        fecha_oficio = datetime.strptime(fecha_oficio_str, '%d/%m/%Y').date() if fecha_oficio_str else None
                        fecha_auto = datetime.strptime(fecha_auto_str, '%d/%m/%Y').date() if fecha_auto_str else None
                        fecha_registro = datetime.strptime(fecha_registro_str, '%d/%m/%Y').date() if fecha_registro_str else None
                        doc_presentado_fecha = datetime.strptime(doc_presentado_fecha_str, '%d/%m/%Y').date() if doc_presentado_fecha_str else None
                        hora_registro = datetime.strptime(hora_registro_str, '%I:%M %p').time() if hora_registro_str else time(0, 0)

                        existing_gravamen = Gravamen.objects.filter(
                            folio=int(folio),
                            num_oficio=num_oficio,
                            fecha_oficio=fecha_oficio
                        ).first()

                        if existing_gravamen:
                            sql_logs.append(f"Record already exists: {row}")
                            continue
                        else:
                                all_exist = False 
                                # Create Gravamen instance
                                Gravamen.objects.create(
                                    building=selected_building,
                                    folio=int(folio),
                                    edificio=edificio,
                                    organo_levantamiento=organo_levantamiento,
                                    nombre_organo=nombre_organo,
                                    provincia_organo=provincia_organo,
                                    num_oficio=num_oficio,
                                    fecha_oficio=fecha_oficio,
                                    num_auto=num_auto,
                                    fecha_auto=fecha_auto,
                                    descripcion=descripcion,
                                    titular_baja_nombre=titular_baja_nombre,
                                    titular_baja_derecho=titular_baja_derecho,
                                    fecha_registro=fecha_registro,
                                    hora_registro=hora_registro,
                                    num_entrada=num_entrada,
                                    doc_presentado_tipo=doc_presentado_tipo,
                                    doc_presentado_fecha=doc_presentado_fecha, 
                                    nombre_juez=nombre_juez,
                                    derechos_registro=derechos_registro,
                                    nombre_archivo_pdf=nombre_archivo_pdf,
                                    contenido_pdf=contenido_pdf
                                )

                    if all_exist:
                      self.message_user(request, "Data already exist.")
                    else:
                        self.message_user(request, "CSV file imported successfully.")
                    return redirect("..")     
                
                except Exception as e:
                    error_logs = str(e)
                    messages.error(request, f"Error importing CSV file: {e}")
                    return render(request, "admin/csv_import_result.html", {
                        'sql_logs': sql_logs,
                        'error_logs': error_logs,
                        'form': form,
                    })
        else:
            form = CsvImportForm()

        return render(request, 'admin/csv_form.html', {'form': form, 'title': 'Import Gravamenes CSV File'})

@admin.register(Remate)
class RemateAdmin(admin.ModelAdmin):
    list_display = ('folio', 'edificio', 'fecha_acta_remate', 'num_auto', 'building')
    search_fields = ['edificio', 'fecha_acta_remate', 'num_auto', 'building__name']
    actions = ['import_remate_csv']
    change_list_template = "admin/remate_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-remate-csv/', self.admin_site.admin_view(self.import_remate_csv))
        ]
        return custom_urls + urls

    def import_remate_csv(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                selected_building = form.cleaned_data['building']
                try:
                    rows = CsvUtils.read_csv(csv_file)
                    all_exist = True
                    sql_logs = []
                    for row in rows:
                        (folio, edificio, organo_remate, nombre_organo, provincia_organo, 
                        num_acta_remate, fecha_acta_remate_str, num_auto, fecha_auto_str, 
                        num_oficio, fecha_oficio_str, observaciones, titular_baja_nombre, 
                        titular_baja_cedula, titular_baja_derecho, nuevo_titular_nombre, 
                        nuevo_titular_derecho, fecha_registro_str, hora_registro_str, 
                        doc_presentado_tipo, doc_presentado_num, doc_presentado_fecha_str, 
                        num_entrada, nombre_juez, derechos_registro, nombre_archivo_pdf, 
                        contenido_pdf) = row

                        # Convert date strings to date objects
                        fecha_acta_remate = datetime.strptime(fecha_acta_remate_str, '%d/%m/%Y').date() if fecha_acta_remate_str else None
                        fecha_auto = datetime.strptime(fecha_auto_str, '%d/%m/%Y').date() if fecha_auto_str else None
                        fecha_oficio = datetime.strptime(fecha_oficio_str, '%d/%m/%Y').date() if fecha_oficio_str else None
                        fecha_registro = datetime.strptime(fecha_registro_str, '%d/%m/%Y').date() if fecha_registro_str else None
                        doc_presentado_fecha = datetime.strptime(doc_presentado_fecha_str, '%d/%m/%Y').date() if doc_presentado_fecha_str else None

                        # Convert time strings to time objects
                        hora_registro =  TimeUtils.parse_time(hora_registro_str) if hora_registro_str else time(0, 0)

                        existing_remate = Remate.objects.filter(
                            folio=int(folio),
                            num_oficio=num_oficio,
                            fecha_oficio=fecha_oficio
                        ).first()

                        if existing_remate:
                            sql_logs.append(f"Record already exists: {row}")
                            continue
                        else:
                            print('Testing')
                            all_exist = False 
                            # Create Remate instance
                            Remate.objects.create(
                                building=selected_building,
                                folio=int(folio),
                                edificio=edificio,
                                organo_remate=organo_remate,
                                nombre_organo=nombre_organo,
                                provincia_organo=provincia_organo,
                                num_acta_remate=num_acta_remate,
                                fecha_acta_remate=fecha_acta_remate,
                                num_auto=num_auto,
                                fecha_auto=fecha_auto,
                                num_oficio=num_oficio,
                                fecha_oficio=fecha_oficio,
                                observaciones=observaciones,
                                titular_baja_nombre=titular_baja_nombre,
                                titular_baja_cedula=titular_baja_cedula,
                                titular_baja_derecho=titular_baja_derecho,
                                nuevo_titular_nombre=nuevo_titular_nombre,
                                nuevo_titular_derecho=nuevo_titular_derecho,
                                fecha_registro=fecha_registro,
                                hora_registro=hora_registro,
                                doc_presentado_tipo=doc_presentado_tipo,
                                doc_presentado_num=doc_presentado_num,
                                doc_presentado_fecha=doc_presentado_fecha,
                                num_entrada=num_entrada,
                                nombre_juez=nombre_juez,
                                derechos_registro=derechos_registro,
                                nombre_archivo_pdf=nombre_archivo_pdf,
                                contenido_pdf=contenido_pdf
                            )

                    if all_exist:
                        self.message_user(request, "Data already exist.")
                    else:
                        self.message_user(request, "CSV file imported successfully.")
                    return redirect("..")     
                
                except Exception as e:
                    error_logs = str(e)
                    messages.error(request, f"Error importing CSV file: {e}")
                    return render(request, "admin/csv_import_result.html", {
                        'sql_logs': sql_logs,
                        'error_logs': error_logs,
                        'form': form,
                    })
        else:
            form = CsvImportForm()

        return render(request, 'admin/csv_form.html', {'form': form, 'title': 'Import Remates CSV File'})