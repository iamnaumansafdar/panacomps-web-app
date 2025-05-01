from datetime import datetime, timedelta, timezone
from django.db.models import Q
from .models import Metrics, PDFRawData, MetricsHistory, PDFRawDataHistory
import csv
from io import StringIO
from django.db.models import FloatField
from django.db.models.functions import Cast
import openpyxl
from openpyxl.styles import PatternFill
from django.http import HttpResponse
from django.utils.timezone import now
import statistics
from decimal import Decimal
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from django.shortcuts import get_object_or_404
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from django.conf import settings
from django.db.models import Q
from django.db.models.functions import Trim, Lower, Upper
from django.db.models import F, Q, FloatField
from django.db.models.functions import Cast
from django.db.models.functions import Concat, Trim, Upper
from django.db.models import CharField, Value

class PanaCompsData:
    def get_folio_data(folio):
        pdf_raw_data = PDFRawData.objects.filter(folio__folio=folio)
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        pdf_files = []

        for pdf_data in pdf_raw_data:
            s3_url = pdf_data.get_s3_file_url()
            file_path = pdf_data.get_s3_file_path()
            file_exists = False

            if s3_url:
                file_exists = True
                print(file_exists, 's3_url exists, setting file_exists to True')
                # try:
                #     print('Trying to check existence in S3')
                #     s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_path)
                #     file_exists = True
                #     print('File found in S3')
                # except ClientError as e:
                #     print('File not found in S3')
                #     print('Exception:', e.response['Error']['Message'])
                #     file_exists = False
            else:
                file_exists = False
            pdf_files.append({
                'filename': pdf_data.filename,
                'pdf_text': pdf_data.pdf_text,
                's3_url': s3_url,
                # 'file_exists': file_exists
            })

        metrics = Metrics.objects.filter(folio__folio=folio).values(
            "domicilio",
            "folio__folio",
            "municipio",
            "codigo_ubicacion",
            "fecha_de_construccion",
            "fecha_de_ocupacion",
            "propietarios",
            "sales_transaction_date",
            "valor",
            "valor_del_terreno",
            "valor_de_mejoras",
            "valor_del_traspaso",
            "superficie_inicial",
            "price_per_square_meter",
            "hipoteca",
            "monto",
            "tasa_efectiva",
            "tasa_nominal",
            "interes_anual",
            "feci",
            "interes_anual_feci",
            "nombre",
            "timestamp",
            "uso_del_suelo",
            "edificio",
        )

        return {
            "pdf_raw_data": pdf_files,
            "metrics": list(metrics),
            "file_exists": file_exists
        }
    # def get_folio_data(folio):
    #     pdf_raw_data = PDFRawData.objects.filter(folio__folio=folio)
    #     # for pdf_data in pdf_raw_data:
    #     #     s3_url = pdf_data.get_s3_file_url()
    #     #     print(s3_url, 's3_url')
    #     # s3_client = boto3.client('s3')
    #     s3_client = boto3.client(
    #         's3',
    #         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    #         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    #         region_name=settings.AWS_S3_REGION_NAME,
    #     )

    #     s3_url = None
    #     file_exists = False

    #     for pdf_data in pdf_raw_data:
    #         print(pdf_data.filename, 'pdf file name')
    #         s3_url = pdf_data.get_s3_file_url()
    #         print(s3_url, 's3_url')
    #         file_path = pdf_data.get_s3_file_path()
            
    #         if s3_url:
    #             try:
    #                 s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_path)
    #                 print(s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_path))
    #                 file_exists = True
    #                 print(file_exists, 'file_exists')
    #             except ClientError:
    #                 print('ELse')
    #                 file_exists = False
    #                 break  # Break the loop if any file is not found
    #     metrics = Metrics.objects.filter(folio__folio=folio)
    #     metrics_data = list(
    #         metrics.values(
    #             "domicilio",
    #             "folio__folio",
    #             "municipio",
    #             "codigo_ubicacion",
    #             "fecha_de_construccion",
    #             "fecha_de_ocupacion",
    #             "propietarios",
    #             "sales_transaction_date",
    #             "valor",
    #             "valor_del_terreno",
    #             "valor_de_mejoras",
    #             "valor_del_traspaso",
    #             "superficie_inicial",
    #             "price_per_square_meter",
    #             "hipoteca",
    #             "monto",
    #             "tasa_efectiva",
    #             "tasa_nominal",
    #             "interes_anual",
    #             "feci",
    #             "interes_anual_feci",
    #             "nombre",
    #             "timestamp",
    #             "uso_del_suelo",
    #             "edificio",
    #         )
    #     )

    #     return {
    #         "pdf_raw_data": list(pdf_raw_data.values("filename", "pdf_text")),
    #         "metrics": metrics_data,
    #         "s3_url":s3_url,
    #         "file_exists": file_exists
    #     }
    
    def get_view_history_detial_data(folio):
        pdf_raw_data = PDFRawDataHistory.objects.filter(pdf_data__folio__folio=folio)
        metrics = MetricsHistory.objects.filter(metric__folio__folio=folio)
        print(metrics, 'Metric', folio)
        metrics_data = list(
            metrics.values(
                "domicilio",
                "metric__folio__folio",
                "municipio",
                "codigo_ubicacion",
                "fecha_de_construccion",
                "fecha_de_ocupacion",
                "propietarios",
                "sales_transaction_date",
                "valor",
                "valor_del_terreno",
                "valor_de_mejoras",
                "valor_del_traspaso",
                "superficie_inicial",
                "price_per_square_meter",
                "hipoteca",
                "monto",
                "tasa_efectiva",
                "tasa_nominal",
                "interes_anual",
                "feci",
                "interes_anual_feci",
                "nombre",
                "timestamp",
                "uso_del_suelo",
                "edificio",
            )
        )

        return {
            "pdf_raw_data": list(pdf_raw_data.values("filename", "pdf_text")),
            "metrics": metrics_data,
        }


    def filter_metrics(query_params):
        queryset = Metrics.objects.all()

        min_sales_price = query_params.get("min_sales_price")
        max_sales_price = query_params.get("max_sales_price")
        min_sq_meter = query_params.get("min_sq_meter")
        max_sq_meter = query_params.get("max_sq_meter")
        building = query_params.get("building")
        unit = query_params.get("unit")
        folio = query_params.get("folio")
        date_range = query_params.get("date_range")

        print(building, 'Paras')
            
        if min_sales_price:
                min_sales_price = float(min_sales_price)
                queryset = queryset.filter(valor_del_traspaso__gte=min_sales_price)

        if max_sales_price:
                max_sales_price = float(max_sales_price)
                queryset = queryset.filter(
                    Q(valor_del_traspaso__lte=max_sales_price) | Q(valor_del_traspaso__isnull=True)
                )

        # Ensure min_sq_meter is valid
        if min_sq_meter:
            min_sq_meter = float(min_sq_meter)
            queryset = queryset.exclude(superficie_inicial="")
            queryset = queryset.annotate(superficie_inicial_float=Cast('superficie_inicial', FloatField()))
            queryset = queryset.filter(superficie_inicial_float__gte=min_sq_meter)

        # Ensure max_sq_meter is valid
        if max_sq_meter:
                max_sq_meter = float(max_sq_meter)
                queryset = queryset.exclude(superficie_inicial="")
                queryset = queryset.annotate(superficie_inicial_float=Cast('superficie_inicial', FloatField()))
                queryset = queryset.filter(superficie_inicial_float__lte=max_sq_meter)

        if min_sales_price  and max_sales_price:
            queryset = queryset.filter(
                Q(valor_del_traspaso__gte=min_sales_price) &
                (Q(valor_del_traspaso__lte=max_sales_price) | Q(valor_del_traspaso__isnull=True))
            )

        if min_sq_meter  and max_sq_meter:
            queryset = queryset.filter(
                superficie_inicial_float__gte=min_sq_meter,
                superficie_inicial_float__lte=max_sq_meter,
            )


        if building:
            # queryset = Metrics.objects.all().annotate(
            #     edificio_trimmed=Trim(Upper('edificio')),
            #     building_name_trimmed=Trim(Upper('building__name')),
            #     combined_name=Concat(
            #         F('building_name_trimmed'), Value(' '), F('edificio_trimmed'),
            #         output_field=CharField()
            #     )
            # )
            # queryset = queryset.filter(Q(combined_name__icontains=building.strip()))
            queryset = queryset.filter(Q(building__name__icontains=building.strip()))


        if unit:
            queryset = queryset.filter(domicilio=unit)

        if folio:
            queryset = queryset.filter(folio__folio__exact=folio)

        if date_range:
            
            start_date, end_date = date_range.split(" - ")
            start_date_formatted = datetime.strptime(start_date, "%d/%m/%Y").strftime(
                "%Y-%m-%d"
            )
            end_date_formatted = datetime.strptime(end_date, "%d/%m/%Y").strftime(
                "%Y-%m-%d"
            )
            queryset = queryset.filter(
                Q(sales_transaction_date__range=[start_date_formatted, end_date_formatted]) |
                Q(sales_transaction_date__isnull=True, edificio__icontains=building.strip())
                )
        return queryset   

        

    def format_date_range(date_range):
        if not date_range:
            return None, None
        
        # print(f"Received date_range: {date_range}")

        try:
            start_date, end_date = date_range.split(" - ")
        except ValueError as e:
            print(f"Error splitting date_range: {e}")
            return None, None

        # print(f"Parsed start_date: {start_date}, end_date: {end_date}")

        try:
            start_date_format = datetime.strptime(start_date, "%d/%m/%Y").strftime("%d/%m/%Y")
            end_date_format = datetime.strptime(end_date, "%d/%m/%Y").strftime("%d/%m/%Y")
        except ValueError as e:
            print(f"Error parsing dates: {e}")
            return None, None

        # print(f"Formatted start_date: {start_date_format}, end_date: {end_date_format}")

        return start_date_format, end_date_format

    def generate_PenaComps_csv():
        metrics_data = Metrics.objects.all()
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer)

        # Write the header row
        csv_writer.writerow(
            [
                "Folio",
                "Codigo Ubicacion",
                "Municipio",
                "Edificio",
                "Fecha De Construccion",
                "Fecha De Ocupacion",
                "Propietarios",
                "Domicilio",
                "Sales Transaction Date",
                "Valor",
                "Valor Del Terreno",
                "valor_de_mejoras",
                "valor_del_traspaso",
                "superficie_inicial",
                "price_per_square_meter",
                "hipoteca",
                "Monto",
                "tasa_efectiva",
                "tasa_nominal",
                "interes_anual",
                "feci",
                "interes_anual_feci",
                "nombre",
                "timestamp",
            ]
        )

        # Write each row of metrics data to the CSV buffer
        for metric in metrics_data:
            csv_writer.writerow(
                [
                    metric.folio,
                    metric.codigo_ubicacion,
                    metric.municipio,
                    metric.edificio,
                    metric.fecha_de_construccion,
                    metric.fecha_de_ocupacion,
                    metric.propietarios,
                    metric.domicilio,
                    metric.sales_transaction_date,
                    metric.valor,
                    metric.valor_del_terreno,
                    metric.valor_de_mejoras,
                    metric.valor_del_traspaso,
                    metric.superficie_inicial,
                    metric.price_per_square_meter,
                    metric.hipoteca,
                    metric.monto,
                    metric.tasa_efectiva,
                    metric.tasa_nominal,
                    metric.interes_anual,
                    metric.feci,
                    metric.interes_anual_feci,
                    metric.nombre,
                    metric.timestamp,
                ]
            )

        # Reset the buffer pointer to the beginning
        csv_buffer.seek(0)

        return csv_buffer
    

    def determine_color(price, mean_price, std_dev_price):
        
        mean_price = float(mean_price)
        std_dev_price = float(std_dev_price)
        print(mean_price, 'mean_price')
        print(std_dev_price, 'std_dev_price')
        if price is None:
            return "#D3D3D3"  # Light Gray for "NO DATA"
        price = float(price)
        print(price, 'price')
        deviation = (price - mean_price) / std_dev_price if std_dev_price != 0 else 0
        print(deviation, 'deviation1')
        if deviation > 1:
            return "#FF4500"  # Red for extremely high
        elif deviation > 0.5:
            return "#FFA500"  # Orange for high
        elif -0.5 <= deviation <= 0.5:
            return "#FFFF00"  # Yellow for average
        elif deviation < -1:
            return "#32CD32"  # Green for extremely low
        else:
            return "#90EE90"  # Light Green for very low
        



    def calculate_average_price(metrics):
        total_price = 0
        total_metros = 0
        for metric in metrics:
            # valor_del_traspaso = metric.valor_del_traspaso
            # price_per_square_meter = metric.superficie_inicial
            valor_del_traspaso = ColorCodeLogic.convert_price_to_number(metric.valor_del_traspaso)
            price_per_square_meter = ColorCodeLogic.convert_price_to_number(metric.superficie_inicial)
            if valor_del_traspaso and price_per_square_meter:
                total_price += valor_del_traspaso
                total_metros += price_per_square_meter

        average_price = total_price / total_metros if total_metros > 0 else 0

        # Convert to formatted string
        formatted_average_price = f"B/. {average_price:.2f}"
        return formatted_average_price
    
    def total_calculate_average_price(total_building):
        queryset = Metrics.objects.all()
        if total_building:
            queryset = queryset.filter(Q(building__name__icontains=total_building.strip()))
            # queryset = Metrics.objects.all().annotate(
            #     edificio_trimmed=Trim(Upper('edificio')),
            #     building_name_trimmed=Trim(Upper('building__name')),
            #     combined_name=Concat(
            #         F('building_name_trimmed'), Value(' '), F('edificio_trimmed'),
            #         output_field=CharField()
            #     )
            # )
            # queryset = queryset.filter(Q(combined_name__icontains=total_building.strip()))


        total_price = 0
        total_metros = 0
        for metric in queryset:
            # valor_del_traspaso = metric.valor_del_traspaso
            # price_per_square_meter = metric.superficie_inicial
            valor_del_traspaso = ColorCodeLogic.convert_price_to_number(metric.valor_del_traspaso)
            price_per_square_meter = ColorCodeLogic.convert_price_to_number(metric.superficie_inicial)
            if valor_del_traspaso and price_per_square_meter:
                total_price += valor_del_traspaso
                total_metros += price_per_square_meter

        average_price = total_price / total_metros if total_metros > 0 else 0

        # Convert to formatted string
        total_formatted_average_price = f"B/. {average_price:.2f}"
        return total_formatted_average_price
    

    def format_datetime_with_utc(dt):
        if dt is not None:
            dt = dt.astimezone(timezone.utc)  # Convert to UTC timezone
            return dt.strftime('%d/%m/%Y %H:%M:%S %Z')  # Format with date, time, and timezone
        return 'None'



class ColorCodeLogic:
   
   @staticmethod
   def convert_price_to_number(value):
        # print(value, 'value')
        if isinstance(value, str):
            value = value.replace('B/.', '').replace(',', '').replace('$', '').strip()
            # value = value.replace(',', '').replace('$', '').strip()
            try:
                number = float(value)
                return number
            except Exception as e:
                # print(f"Error converting value '{value}': {e}")
                return 0
        elif isinstance(value, Decimal):
            number = float(value)
            return number
        elif isinstance(value, (int, float)):
            return value
        return 0
   
   @staticmethod 
   def convert_price_to_number1(value):
        if value is None:
            return 0

        if isinstance(value, str):
            value = value.replace('B/.', '').replace(',', '').replace('$', '').strip()
            try:
                number = float(value)
                return number
            except ValueError:
                return 0
        else:
            try:
                number = float(value)
                return number
            except (TypeError, ValueError):
                return 0




   @staticmethod
   def calculate_and_insert_average_sales_price(sheet, valor_col_index, metros_col_index):
        total_price = 0
        total_metros = 0

        for row in sheet.iter_rows(min_row=4, min_col=1, max_col=sheet.max_column):
        
            metros_value = row[valor_col_index - 1].value
            valor_value = row[metros_col_index - 1].value
            # print(f"Row {row[0].row} - METROS CUADRADOS: {metros_value}, VALOR DEL TRASPASO: {valor_value}")

            metros = ColorCodeLogic.convert_price_to_number(metros_value)  # Square Meters
            valor = ColorCodeLogic.convert_price_to_number1(valor_value)  # Sale Amount

            # print('Converted - METROS CUADRADOS:', metros, 'VALOR DEL TRASPASO:', valor)

            # if valor is not None and metros is not None:
            total_price += valor
            total_metros += metros

        # Avoid division by zero
        average_price = total_price / total_metros if total_metros > 0 else 0

        # Format the average price
        formatted_average_price = f"B/. {average_price:.2f}"

        # Add the average price to the spreadsheet
        last_row = sheet.max_row

        # Setting the label in Panamanian Spanish and English
        spanish_label = "Precio Promedio Ponderado de Venta por Metro Cuadrado"
        english_label = "(Weighted Average Sales Price per Square Meter)"

        average_label_cell_spanish = sheet.cell(row=last_row + 2, column=valor_col_index+1)
        average_value_cell = sheet.cell(row=last_row + 3, column=valor_col_index + 2)
        average_label_cell_english = sheet.cell(row=last_row + 3, column=valor_col_index+1)

        average_label_cell_spanish.value = spanish_label
        average_label_cell_english.value = english_label
        average_value_cell.value = formatted_average_price

        # Formatting
        average_label_cell_spanish.alignment = Alignment(horizontal='right')
        average_label_cell_english.alignment = Alignment(horizontal='right')
        average_value_cell.alignment = Alignment(horizontal='center')
        average_label_cell_spanish.font = Font(name="Helvetica Neue", size=18, bold=True)
        average_label_cell_english.font = Font(name="Helvetica Neue", size=18)
        average_value_cell.font = Font(name="Helvetica Neue", size=18)

        thin_border = Border(left=Side(style='thin'),
                            right=Side(style='thin'),
                            top=Side(style='thin'),
                            bottom=Side(style='thin'))
        average_value_cell.border = thin_border


   @staticmethod
   def color_code_prices_with_shades(ws, precio_col_index):
        prices = []
        max_row_with_data = ws.max_row - 3
        for row in ws.iter_rows(min_row=4,max_row=max_row_with_data,  min_col=precio_col_index, max_col=precio_col_index):
            cell = row[0]
            price = ColorCodeLogic.convert_price_to_number(cell.value)
            # print(f"Row: {cell.row}, Original Value: {cell.value}, Converted Price: {price}")
            if price is not None:
                prices.append(price)
        if not prices:
            print("No valid prices found.")
            return
        # print(prices, 'pppp1')
        mean_price = statistics.mean(prices)
        std_dev_price = statistics.stdev(prices) if len(prices) > 1 else 0
        # print(mean_price, 'mean_price')
        # print(std_dev_price, 'std_dev_price')

        for row in ws.iter_rows(min_row=4, min_col=precio_col_index, max_col=precio_col_index):
                cell = row[0]
                # print(cell.value, 'cell')
                price = ColorCodeLogic.convert_price_to_number(cell.value)
                # print(price, 'price')
                if price == 0:
                    color = "D3D3D3"  # Light Gray for "NO DATA"
                else:
                    deviation = (price - mean_price) / std_dev_price if std_dev_price != 0 else 0
                    # print(deviation, 'deviation')
                    if deviation > 1:
                        color = "FF4500"  # Red for extremely high
                    elif deviation > 0.5:
                        color = "FFA500"  # Orange for high
                    elif -0.5 <= deviation <= 0.5:
                        color = "FFFF00"  # Yellow for average
                    elif deviation < -1:
                        color = "32CD32"  # Green for extremely low
                    else:
                        color = "90EE90"  # Light Green for very low
                cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")


   @staticmethod
   def trim_domicilio_values(sheet, domicilio_col_index):
        """
        Trims the values in the 'DOMICILIO' column to only include information up to 'EDIFICIO'.
        If 'EDIFICIO' is not found, the value is left as-is.
        """
        for row in sheet.iter_rows(min_row=4, min_col=domicilio_col_index, max_col=domicilio_col_index):
            cell = row[0]  # Get the first (and only) cell in the tuple
            value = cell.value
            if value and 'EDIFICIO' in value:
                # Trim the value up to the word 'EDIFICIO', excluding it
                trimmed_value = value.split('EDIFICIO')[0].rstrip(', ')
                cell.value = trimmed_value

   @staticmethod
   def trim_unit_values(sheet, domicilio_col_index):
        for row in sheet.iter_rows( min_col=domicilio_col_index, max_col=domicilio_col_index):
            cell = row[0]  
            value = cell.value
            if value and 'EDIFICIO' in value:
                trimmed_value = value.split('EDIFICIO')[0].rstrip(', ')
                cell.value = trimmed_value

    
   @staticmethod
   def parse_date_string(date_str):
        try:
            return datetime.strptime(date_str, "%d/%m/%Y")
        except:
            return None
    
   @staticmethod
   def sort_by_date(sheet, date_col_index):
        data_rows = [
            [cell.value for cell in row]
            for row in sheet.iter_rows(min_row=4, max_row=sheet.max_row)
        ]

        # Parse the date strings into datetime objects for sorting
        for row in data_rows:
            date_str = row[date_col_index - 1]
            # Use the earliest representable date if parsing fails
            row[date_col_index - 1] = ColorCodeLogic.parse_date_string(date_str) or datetime.min

        # Sort the rows by the date column in descending order (most recent first)
        data_rows.sort(key=lambda r: (
            r[date_col_index - 1] is not None, r[date_col_index - 1]), reverse=True)

        # Write the sorted rows back into the worksheet, starting from row 2
        for row_idx, row in enumerate(data_rows, start=4):
            for col_idx, value in enumerate(row, start=1):
                cell = sheet.cell(row=row_idx, column=col_idx)
                # Check if the date is the minimum date, and replace it with "NO DATE"
                if isinstance(value, datetime) and value == datetime.min:
                    cell.value = "NO DATE"
                else:
                    cell.value = value if not isinstance(
                        value, datetime) else value.strftime("%d/%m/%Y")

   @staticmethod
   def adjust_column_widths(sheet):
        for col_idx, col in enumerate(sheet.iter_cols(min_col=1, max_col=sheet.max_column), start=1):
            max_length = 0
            column_letter = get_column_letter(col_idx)
            for cell in col:
                try:
                    if cell.value is not None and len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            sheet.column_dimensions[column_letter].width = (max_length + 2) * 2.0
 





def parse_integer(value):
    if value and value != '':
        try:
            return int(float(value))  
        except ValueError:
            return None  
    return None


def parse_datetime(value):
    if value and value != '':
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            try:
                # If that fails, try without microseconds
                return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    return datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    return None  
    return None

