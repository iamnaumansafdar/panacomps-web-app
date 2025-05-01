import csv
import json
import openpyxl
import statistics
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from django.views.generic import View
from .models import Metrics, PDFRawData, MetricsHistory, BarriosEdificios, Building
from .utils import PanaCompsData, ColorCodeLogic
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from django.db.models import Q
from django.db.models.functions import Trim, Lower, Upper
from django.db.models import F, Q, FloatField
from django.db.models.functions import Cast
from django.utils.timezone import now
from openpyxl.styles import PatternFill
from django.http import HttpResponse
from django.utils.timezone import now
from openpyxl.styles import PatternFill
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from accounts.models import GroupProfile
from contact.models import GlossaryTerm, AIPromptTemplate
from django.db.models import OuterRef, Subquery
from django.db.models import F, Value
from django.db.models.functions import Concat, Trim, Upper
from django.db.models import CharField, Value
# Create your views here.



class PanacompsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "home/index.html"
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["user"] = user
        context["subscription_level"] = user.subscription_level
        metrics_queryset = Metrics.objects.all().distinct()
        user = self.request.user
        group_profile = None
        enable_ai_analysis = False


        if user.is_superuser:
            can_download_pdf = True
            enable_ai_analysis = True
        else:    
            user_group = user.groups.first()
            try:
                group_profile = GroupProfile.objects.get(group=user_group)
                print(group_profile, 'profile')
                enable_ai_analysis = group_profile.enable_ai_analysis
            except GroupProfile.DoesNotExist:
                pass
            if group_profile:
                can_download_pdf = group_profile.can_download_pdf
            else:
                can_download_pdf = True   
        
        municipios = Metrics.objects.values_list('municipio', flat=True).distinct().order_by('municipio')
        context['municipios'] = municipios
        
        
        # Step 1: Get distinct `edificio` and `building.name` from the `Metrics` table
        # metrics_with_building_names = Metrics.objects.annotate(
        #     edificio_trimmed=Trim(Upper('edificio')), 
        #     building_name_trimmed=Trim(Upper('building__name')) 
        # ).annotate(
        #     combined_name=Concat(  
        #         F('building_name_trimmed'), Value(' '), F('edificio_trimmed'),
        #         output_field=CharField()  
        #     )
        # ).values_list('combined_name', flat=True).distinct().order_by('combined_name')

        # Step 2: Print the combined results
        # print(metrics_with_building_names, 'combined names')
        # context['metrics_with_building_names'] = metrics_with_building_names

        dropdown_buildings = Metrics.objects.filter(
            building__isnull=False  # To ensure only Metrics with a linked building are retrieved
        ).annotate(
            trimmed_name=Trim(Upper('building__name'))  # Trim and uppercase for consistency
        ).values_list('trimmed_name', flat=True).distinct().order_by('trimmed_name')
        print(dropdown_buildings, 'dropdown_buildings')
        context['dropdown_buildings'] = dropdown_buildings
        



        buildings = Metrics.objects.annotate(
                trimmed_name=Trim(Upper('edificio'))
            ).values_list('trimmed_name', flat=True).distinct().order_by('trimmed_name')

        try:
            if group_profile.accessible_buildings.exists():
            #    dropdown_buildings = group_profile.accessible_buildings.all()
               metrics_queryset = group_profile.accessible_buildings.select_related('building').all()
               building_names = metrics_queryset.values_list('building__name', flat=True).distinct()
               dropdown_buildings = Building.objects.filter(name__in=building_names).order_by('name')
               print(dropdown_buildings, 'Access BUilding')
        except:
            pass    
        context['dropdown_buildings'] = dropdown_buildings

        metrics_queryset = metrics_queryset.order_by('-sales_transaction_date')

        # Pagination
        paginator = Paginator(metrics_queryset, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            metrics = paginator.page(page)
        except PageNotAnInteger:
            metrics = paginator.page(1)
        except EmptyPage:
            metrics = paginator.page(paginator.num_pages)

         
        # Fetch neighborhoods
        barrios = BarriosEdificios.objects.all().order_by('nombre_barrio')
        context['barrios'] = barrios
        context['metrics'] = metrics
        context['can_download_pdf'] = can_download_pdf
        context['metric_count'] = metrics_queryset.count()
        context['total_metric_count'] = Metrics.objects.all().count()
        context['page_obj'] = metrics 
        context['glossary_terms'] = GlossaryTerm.objects.all()
        context['ai_prompt_templates'] = AIPromptTemplate.objects.all()
        context['enable_ai_analysis'] = enable_ai_analysis
        return context


def filter_units_and_folios(request):
    building = request.GET.get('building')
    date_range = request.GET.get('date_range')

    queryset = Metrics.objects.all()
    if building:
        building = building.strip()
        # queryset = Metrics.objects.all().annotate(
        #         edificio_trimmed=Trim(Upper('edificio')),
        #         building_name_trimmed=Trim(Upper('building__name')),
        #         combined_name=Concat(
        #             F('building_name_trimmed'), Value(' '), F('edificio_trimmed'),
        #             output_field=CharField()
        #         )
        #     )
        # queryset = queryset.filter(Q(combined_name__icontains=building.strip()))
        queryset = queryset.filter(Q(building__name__icontains=building))
        

    if date_range:
        start_date, end_date = date_range.split(" - ")
        start_date_formatted = datetime.strptime(start_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        end_date_formatted = datetime.strptime(end_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        queryset = queryset.filter(
                Q(sales_transaction_date__range=[start_date_formatted, end_date_formatted]) |
                Q(sales_transaction_date__isnull=True, edificio__icontains=building.strip())
                )

    units = queryset.values_list('domicilio', flat=True).distinct().order_by('domicilio')
    folios = queryset.values_list('folio__folio', flat=True).distinct().order_by('-folio__folio')
    print(units.count(), folios.count(), 'Checking')
    # truncated_units = [unit[:50] for unit in units]

    return JsonResponse({
        'units': list(units),
        'folios': list(folios),
    })


def filter_region_view(request):
    # region = request.GET.get('region')
    neighborhood = request.GET.get('neighborhood')
    date_range = request.GET.get('date_range')

    queryset = Metrics.objects.all()

    # if region and region.strip().upper() != "ALL":
    #     queryset = queryset.filter(Q(municipio__icontains=region.strip()))  

    if neighborhood and neighborhood.strip().upper() != "ALL":
        queryset = queryset.filter(building__nombre_barrio__nombre_barrio__icontains=neighborhood.strip())
  
        

    if date_range:
        start_date, end_date = date_range.split(" - ")
        start_date_formatted = datetime.strptime(start_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        end_date_formatted = datetime.strptime(end_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        queryset = queryset.filter(
                Q(sales_transaction_date__range=[start_date_formatted, end_date_formatted]) 
                # Q(sales_transaction_date__isnull=True, edificio__icontains=region.strip())
                )

    buildings = queryset.values_list('building__name', flat=True).distinct().order_by('building__name')


    # buildings = queryset.annotate(
    #         edificio_trimmed=Trim(Upper('edificio')), 
    #         building_name_trimmed=Trim(Upper('building__name'))  
    #     ).annotate(
    #         combined_name=Concat(  
    #             F('building_name_trimmed'), Value(' '), F('edificio_trimmed'),
    #             output_field=CharField() 
    #         )
    #     ).values_list('combined_name', flat=True).distinct().order_by('combined_name')

        

    return JsonResponse({
        'buildings': list(buildings),
    })


def filter_folios_number(request):
    unit = request.GET.get('unit')
    date_range = request.GET.get('date_range')

    queryset = Metrics.objects.all()
    if unit:
        unit = unit.strip()
        queryset = queryset.filter(Q(domicilio__icontains=unit))
    folios = queryset.values_list('folio__folio', flat=True).distinct().order_by('-folio__folio')


    return JsonResponse({
        'folios': list(folios),
    })

class ViewDetailPanaComps(View):
    def get(self, request):
        folio = request.GET.get("folio")
        data = PanaCompsData.get_folio_data(folio)
        return JsonResponse(data)

class ViewHistoyDetailPanaComps(View):
    def get(self, request):
        folio = request.GET.get("folio")
        data = PanaCompsData.get_view_history_detial_data(folio)
        return JsonResponse(data)

class CheckHistoryView(View):
    def get(self, request):
        folio = request.GET.get("folio")
        metrics = MetricsHistory.objects.filter(metric__folio__folio=folio)
        has_history = metrics.exists()
        return JsonResponse({"has_history": has_history})
    
class DownloadPDFRawDataCSV(View):
    def get(self, request):
        folio = request.GET.get("folio")
        pdf_raw_data = PDFRawData.objects.filter(folio__folio=folio)
        met = Metrics.objects.get(folio__folio=folio)
        building_name = met.edificio

        custom_filename = f"{building_name}_{folio}_PDFData.csv"

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{custom_filename}"'

        writer = csv.writer(response)

        # Add user information and download date to the first row
        user = request.user
        download_date = now().strftime('%d/%m/%Y %H:%M:%S')
        writer.writerow([f'User: {user.first_name} {user.last_name}', f'Downloaded on: {download_date}'])

        # Add an empty row
        writer.writerow([])


        writer.writerow(["Folio", "File Name", "PDF Text"])
        if not pdf_raw_data.exists():
            return HttpResponse("Folio,File Name,PDF Text", content_type="text/csv")

        for data in pdf_raw_data:
            writer.writerow([data.folio.folio, data.filename, data.pdf_text])

        return response


class UpdatePanacompsDashboardView(View):
    paginate_by = 25

    def get(self, request):

        query_params = request.GET
        user = request.user
        
        building = query_params.get("building")
        print(building, 'building')
        total_queryset = Metrics.objects.all()
        # queryset = total_queryset.filter(Q(edificio__icontains=building.strip()))
        queryset = total_queryset.filter(Q(building__name__icontains=building.strip()))
        # queryset = Metrics.objects.all().annotate(
        #         edificio_trimmed=Trim(Upper('edificio')),
        #         building_name_trimmed=Trim(Upper('building__name')),
        #         combined_name=Concat(
        #             F('building_name_trimmed'), Value(' '), F('edificio_trimmed'),
        #             output_field=CharField()
        #         )
        #     )
        # queryset = queryset.filter(Q(combined_name__icontains=building.strip()))

        total_record_count = queryset.count()

        results_per_page = int(query_params.get('results_per_page', 25))
        self.paginate_by = results_per_page 

        queryset = PanaCompsData.filter_metrics(query_params).order_by(
             F('sales_transaction_date').desc(nulls_last=True)
             )

        if queryset.count() < results_per_page:
            self.paginate_by = queryset.count()
        else:
            self.paginate_by = results_per_page

        if user.is_superuser:
            # Admins see all records
            can_download_summary_excel = True
            can_download_detailed_excel = True
            can_download_pdf = True
            can_view_detail = True
            can_view_history = True
        else:
            user_group = user.groups.first()
            group_profile = None
            
            try:
                group_profile = GroupProfile.objects.get(group=user_group)
            except GroupProfile.DoesNotExist:
                print(f"GroupProfile does not exist for group: {user_group}")
                queryset = PanaCompsData.filter_metrics(query_params).order_by(
                F('sales_transaction_date').desc(nulls_last=True)
                )

            if group_profile:
                
                # Apply record limit based on the group's record_limit
                if group_profile.record_limit is not None:
                    queryset = queryset[:group_profile.record_limit]

                # Disable download and view options if not allowed
                can_download_summary_excel = group_profile.can_download_summary_excel
                can_download_detailed_excel = group_profile.can_download_detailed_excel
                can_download_pdf = group_profile.can_download_pdf
                can_view_detail = group_profile.can_view_detail
                can_view_history = group_profile.can_view_history
            else:
                # Default settings for trial or undefined users
                can_download_summary_excel = True
                can_download_detailed_excel = True
                can_download_pdf = True
                can_view_detail = True
                can_view_history = True     

        prices = []
        price_data = []
        for metric in queryset:
            price = metric.price_per_square_meter
            if price is not None:
                prices.append(float(price))
            price_data.append((metric, price))

        if prices:
            print(prices, 'pppp')
            mean_price = statistics.mean(prices)
            std_dev_price = statistics.stdev(prices) if len(prices) > 1 else 0
        else:
            mean_price = std_dev_price = 0

        # Add color information to the queryset
        colored_metrics = []
        for metric, price in price_data:
            color = PanaCompsData.determine_color(price, mean_price, std_dev_price)
            colored_metrics.append((metric, color))    
        

        print(colored_metrics, 'Color Metric')


        start_date_format, end_date_format = PanaCompsData.format_date_range(
            query_params.get("date_range")
        )
        record_count = queryset.count()

        if queryset.count() < results_per_page:
           self.paginate_by = queryset.count() or 1  # Set to 1 if queryset is empty
        else:
            self.paginate_by = results_per_page

        if total_record_count > 0:
            paginator = Paginator(queryset, self.paginate_by)
            page_number = request.GET.get('page')
            
            try:
                metrics = paginator.page(page_number)
            except PageNotAnInteger:
                metrics = paginator.page(1)
            except EmptyPage:
                metrics = paginator.page(paginator.num_pages)
        else:
            metrics = [] 
        formatted_average_price = PanaCompsData.calculate_average_price(metrics)
        print(formatted_average_price, 'formatted_average_price')
        total_building = query_params.get("building")
        total_average_price = PanaCompsData.total_calculate_average_price(total_building)
        color_dict = {metric.id: color for metric, color in colored_metrics}
        context = {"metrics": metrics, 'color_dict':color_dict,
                    'average_price': formatted_average_price,
                    'total_average_price': total_average_price,
                    'can_download_pdf': can_download_pdf,
                    'can_view_detail': can_view_detail,
                    'can_view_history': can_view_history,
                     }

        metric_data = render_to_string("Filters/filter_home_page.html", context=context)

        total_queryset = PanaCompsData.filter_metrics(query_params).order_by(
             F('sales_transaction_date').desc(nulls_last=True)
             )
        print(record_count, 'record_count')
        print(total_record_count, 'total_record_count')

        response_data = {
            "min_sales_price": query_params.get("min_sales_price"),
            "max_sales_price": query_params.get("max_sales_price"),
            "min_sq_meter": query_params.get("min_sq_meter"),
            "max_sq_meter": query_params.get("max_sq_meter"),
            "building": query_params.get("building"),
            "unit": query_params.get("unit"),
            "folio": query_params.get("folio"),
            "start_date_format": start_date_format,
            "end_date_format": end_date_format,
            "record_count": record_count,
            "total_record_count": total_record_count,
            "metric_data": metric_data,
            'average_price': formatted_average_price,
            'total_average_price': total_average_price,
            # 'metrics':metrics
        }
        min_sales_price = query_params.get("min_sales_price")
        max_sales_price = query_params.get("max_sales_price")
        min_sq_meter = query_params.get("min_sq_meter")
        max_sq_meter = query_params.get("max_sq_meter")
        building = query_params.get("building")
        unit = query_params.get("unit")
        folio = query_params.get("folio")
        date_range = query_params.get("date_range")

        pagination_data = render_to_string("Filters/pagination.html", {
        "metrics": metrics, 
        'building': building,
        'min_sales_price':min_sales_price,
        'max_sales_price':max_sales_price,
        'min_sq_meter':min_sq_meter,
        'max_sq_meter':max_sq_meter,
        'unit': unit,
        'folio':folio,
        'date_range':date_range,
        'can_download_summary_excel': can_download_summary_excel,
        'can_download_detailed_excel': can_download_detailed_excel,
        })

        # Append pagination HTML to the response_data
        response_data["pagination_data"] = pagination_data

        return JsonResponse(response_data)

class ResetPanacompsDashboardView(View):
    paginate_by = 30

    def get(self, request):
        query_params = request.GET
        queryset = PanaCompsData.filter_metrics(query_params)

        start_date_format, end_date_format = PanaCompsData.format_date_range(
            query_params.get("date_range")
        )
        record_count = queryset.count()

        filtered_buildings = queryset.order_by("-sales_transaction_date")

        paginator = Paginator(queryset.order_by('-sales_transaction_date'), self.paginate_by)
        page_number = request.GET.get('page')
        
        try:
            metrics = paginator.page(page_number)
        except PageNotAnInteger:
            metrics = paginator.page(1)
        except EmptyPage:
            metrics = paginator.page(paginator.num_pages)

        context = {"metrics": filtered_buildings}

        metric_data = render_to_string("Filters/filter_home_page.html", context=context)

        response_data = {
            "min_sales_price": query_params.get("min_sales_price"),
            "max_sales_price": query_params.get("max_sales_price"),
            "min_sq_meter": query_params.get("min_sq_meter"),
            "max_sq_meter": query_params.get("max_sq_meter"),
            "building": query_params.get("building"),
            "unit": query_params.get("unit"),
            "folio": query_params.get("folio"),
            "start_date_format": start_date_format,
            "end_date_format": end_date_format,
            "record_count": record_count,
            "metric_data": metric_data,
            # 'metrics':metrics
        }
        pagination_data = render_to_string("Filters/pagination.html", {"metrics": metrics})

        # Append pagination HTML to the response_data
        response_data["pagination_data"] = pagination_data

        return JsonResponse(response_data)



class DownloadPenaCompsCSV(View):
    def get(self, request, *args, **kwargs):
        # Generate the CSV data
        csv_buffer = PanaCompsData.generate_PenaComps_csv()
        response = HttpResponse(csv_buffer, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="PenaComps_report.csv"'

        return response


class FilterPDFDataView(View):
    def get(self, request):
        filters = json.loads(request.GET.get("filters", "[]"))
        folioId = request.GET.get('folioId')
        # Start with all data
        filtered_data = PDFRawData.objects.filter(folio__folio=folioId)

        # Mapping of front-end field names to model field names
        field_mapping = {
            "filename": "filename",
            "pdftext": "pdf_text"
        }

        for filter in filters:
            file_select = filter.get('fileSelect')
            include_select = filter.get('includeSelect')
            test_input = filter.get('testInput')
            logic_operator = filter.get('logicOperator')


            # Map the front-end field name to the model field name
            file_value = field_mapping.get(file_select)

            if include_select == "includes":
                query = Q(**{f"{file_value}__icontains": test_input})
                print(query, 'query')
            elif include_select == "does_not_include":
                query = ~Q(**{f"{file_value}__icontains": test_input})
            elif include_select == "is":
                query = Q(**{file_value: test_input})
            elif include_select == "is_not":
                query = ~Q(**{file_value: test_input})
            elif include_select == "is_empty":
                query = Q(**{f"{file_value}__isnull": True})
            elif include_select == "is_not_empty":
                query = ~Q(**{f"{file_value}__isnull": True})

            if logic_operator == "And":
                filtered_data = filtered_data.filter(query)
                print(filtered_data, 'And filtered_data')
            elif logic_operator == "Or":
                filtered_data = filtered_data.filter(query) | filtered_data
                print(filtered_data, 'OR filtered_data')

        # Serialize the filtered data
        filtered_data = list(filtered_data.values('filename', 'pdf_text'))

        return JsonResponse({'pdf_data': filtered_data})





class DownloadSearchResultCSVView(View):
    def get(self, request):
        query_params = request.GET
        queryset = PanaCompsData.filter_metrics(query_params)
        queryset = queryset.order_by("-sales_transaction_date")
        user = request.user
        if user.is_superuser:
            queryset = PanaCompsData.filter_metrics(query_params)
            queryset = queryset.order_by("-sales_transaction_date")
        else:    
            user_group = user.groups.first()
            try:
                group_profile = GroupProfile.objects.get(group=user_group)
                if group_profile.record_limit is not None:
                    queryset = queryset[:group_profile.record_limit]
            except GroupProfile.DoesNotExist:
                pass


        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Download Summary"

        # Add user information and download date to the first row
        user = request.user
        download_date = now().strftime('%d/%m/%Y %H:%M:%S')
        ws.append([f'User: {user.first_name} {user.last_name}', f'Downloaded on: {download_date}'])

         # Add an empty row
        ws.append([])

        headers = [  'FOLIO', 'UNIT', 'SALES DATE', 'SQUARE METERS', 'SALES PRICE',
            'PRICE PER SQUARE METER' ]
        
        ws.append(headers)

        for metric in queryset:
            row = [
                metric.folio.folio,
                metric.domicilio,
                metric.sales_transaction_date.strftime('%d/%m/%Y') if metric.sales_transaction_date else '',
                metric.superficie_inicial,
                f"B/.{metric.valor_del_traspaso:,.2f}" if metric.valor_del_traspaso else '',
                f"B/.{metric.price_per_square_meter}" if metric.price_per_square_meter else '',
                # metric.timestamp.strftime('%d/%m/%Y') if metric.timestamp else ''
                 ]
            ws.append(row)
        

        # Determine the index of the "DOMICILIO" column (1-based index)
        domicilio_col_index = headers.index('UNIT') + 1

        # Trim domicilio values
        ColorCodeLogic.trim_unit_values(ws, domicilio_col_index)

        # Find column indices for 'VALOR DEL TRASPASO' and 'Price per square meter'
        valor_col_index = headers.index('SQUARE METERS') + 1
        metros_col_index = headers.index('SALES PRICE') + 1
        print(valor_col_index, metros_col_index, "INDEX")

        # Calculate and insert average sales price
        ColorCodeLogic.calculate_and_insert_average_sales_price(ws, valor_col_index, metros_col_index)


        # Set font, alignment, fill, and border for the entire sheet
        font = Font(name="Helvetica Neue", size=18)
        alignment = Alignment(horizontal="center", vertical="center")
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        fill = PatternFill(start_color="F7F4F4", end_color="F7F4F4", fill_type="solid")

        for row in ws.iter_rows():
            for cell in row:
                cell.font = font
                cell.alignment = alignment
                cell.border = border
                cell.fill = fill

        # Formatting for the first row (header)
        header_fill = PatternFill(start_color="E5EAF4", end_color="E5EAF4", fill_type="solid")
        header_font = Font(name="Helvetica Neue", size=18, bold=True)

        for cell in ws[3]:
            cell.font = header_font
            cell.fill = header_fill

        # Formatting for rows after the header
        row_fill = PatternFill(start_color="F7F4F4", end_color="F7F4F4", fill_type="solid")
        for row in ws.iter_rows(min_row=4):
            for cell in row:
                cell.fill = row_fill

        # Adjust column widths
        ColorCodeLogic.adjust_column_widths(ws)     
        # Determine the index of the "Price per square meter" column (1-based index)
        precio_col_index = headers.index('PRICE PER SQUARE METER') + 1
        ColorCodeLogic.color_code_prices_with_shades(ws, precio_col_index)
        # Save the workbook to an in-memory file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="search_results.xlsx"'
        wb.save(response)
        return response

class DownloadDetailResultExcelView(View):
    def get(self, request):
        query_params = request.GET
        queryset = PanaCompsData.filter_metrics(query_params)
        queryset = queryset.order_by("-sales_transaction_date")
        user = request.user
        if user.is_superuser:
            queryset = PanaCompsData.filter_metrics(query_params)
            queryset = queryset.order_by("-sales_transaction_date")
        else:    
            user_group = user.groups.first()
            try:
                group_profile = GroupProfile.objects.get(group=user_group)
                if group_profile.record_limit is not None:
                    queryset = queryset[:group_profile.record_limit]
            except GroupProfile.DoesNotExist:
                pass

        # Create an in-memory workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Search Results"

        # Add user information and download date to the first row
        user = request.user
        download_date = now().strftime('%d/%m/%Y %H:%M:%S')
        ws.append([f'User: {user.first_name} {user.last_name}', f'Downloaded on: {download_date}'])

        # Add an empty row
        ws.append([])

        # Add headers
        headers = [
            'FOLIO', 'CODIGO UBICACIÓN', 'MUNICIPIO', 'EDIFICIO',
            'FECHA DE CONSTRUCCIÓN', 'FECHA DE OCUPACIÓN', 'PROPIETARIOS', 'DOMICILIO', 
            'FECHA DE VENTA', 'VALOR', 'VALOR DEL TERRENO', 'VALOR DE MEJORAS',
            'METROS CUADRADOS', 'VALOR DEL TRASPASO', 'PRECIO POR METRO CUADRADO', 'USO DEL SUELO', 'HIPOTECA', 
            'MONTO', 'TASA EFECTIVA', 'TASA NOMINAL', 'INTERÉS ANUAL', 'FECI', 'INTERÉS ANUAL + FECI', 
            'NOMBRE', 'MARCA DE TIEMPO', 
        ]
        ws.append(headers)

        # Add data rows
        for metric in queryset:
            row = [
                metric.folio.folio,
                metric.codigo_ubicacion if metric.codigo_ubicacion is not None else '',
                metric.municipio if metric.municipio else '',
                metric.edificio,
                metric.fecha_de_construccion.strftime('%d/%m/%Y') if metric.fecha_de_construccion else '',
                metric.fecha_de_ocupacion.strftime('%d/%m/%Y') if metric.fecha_de_ocupacion else '',
                metric.propietarios if metric.propietarios else '',
                metric.domicilio if metric.domicilio else '',
                metric.sales_transaction_date.strftime('%d/%m/%Y') if metric.sales_transaction_date else '',
                f"B/.{metric.valor:,.2f}" if metric.valor is not None else '',
                f"B/.{metric.valor_del_terreno:,.2f}" if metric.valor_del_terreno is not None else '',
                f"B/.{metric.valor_de_mejoras:,.2f}" if metric.valor_de_mejoras is not None else '',
                metric.superficie_inicial if metric.superficie_inicial else '',
                f"B/.{metric.valor_del_traspaso:,.2f}" if metric.valor_del_traspaso else '',
                # f"B/.{metric.valor_del_traspaso}" if metric.valor_del_traspaso is not None else '',
                f"B/.{metric.price_per_square_meter}" if metric.price_per_square_meter is not None else '',
                metric.uso_del_suelo if metric.uso_del_suelo else '',
                'Yes' if metric.hipoteca else 'No',
                f"B/.{metric.monto:,.2f}" if metric.monto is not None else '',
                f"{metric.tasa_efectiva}" if metric.tasa_efectiva is not None else '',
                f"{metric.tasa_nominal}" if metric.tasa_nominal is not None else '',
                f"B/.{metric.interes_anual}" if metric.interes_anual is not None else '',
                f"B/.{metric.feci}" if metric.feci is not None else '',
                f"B/.{metric.interes_anual_feci}" if metric.interes_anual_feci is not None else '',
                metric.nombre if metric.nombre else '',
                # metric.timestamp.strftime('%d/%m/%Y') if metric.timestamp else 'None',
                PanaCompsData.format_datetime_with_utc(metric.timestamp) if metric.timestamp else '',
                
            ]
            ws.append(row)
        
        
        # Determine the index of the "DOMICILIO" column (1-based index)
        domicilio_col_index = headers.index('DOMICILIO') + 1

        # Trim domicilio values
        ColorCodeLogic.trim_domicilio_values(ws, domicilio_col_index)

        # Find column indices for 'VALOR DEL TRASPASO' and 'Price per square meter'
        valor_col_index = headers.index('METROS CUADRADOS') + 1 #square meter
        metros_col_index = headers.index('VALOR DEL TRASPASO') + 1 #sale amount
        # print(f"Indices - METROS CUADRADOS: {valor_col_index}, VALOR DEL TRASPASO: {metros_col_index}")
        # Calculate and insert average sales price
        ColorCodeLogic.calculate_and_insert_average_sales_price(ws, valor_col_index, metros_col_index)


        # Set font, alignment, fill, and border for the entire sheet
        font = Font(name="Helvetica Neue", size=18)
        alignment = Alignment(horizontal="center", vertical="center")
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        fill = PatternFill(start_color="F7F4F4", end_color="F7F4F4", fill_type="solid")

        for row in ws.iter_rows():
            for cell in row:
                cell.font = font
                cell.alignment = alignment
                cell.border = border
                cell.fill = fill

        # Formatting for the first row (header)
        header_fill = PatternFill(start_color="E5EAF4", end_color="E5EAF4", fill_type="solid")
        header_font = Font(name="Helvetica Neue", size=18, bold=True)

        for cell in ws[3]:
            cell.font = header_font
            cell.fill = header_fill

        # Formatting for rows after the header
        row_fill = PatternFill(start_color="F7F4F4", end_color="F7F4F4", fill_type="solid")
        for row in ws.iter_rows(min_row=4):
            for cell in row:
                cell.fill = row_fill

          # Adjust column widths
        ColorCodeLogic.adjust_column_widths(ws)     

        
        # Sort by date column (assuming 'Sales Transaction Date' is at index 9)
        # sort_by_date(ws, date_col_index=9) 

        # Determine the index of the "Price per square meter" column (1-based index)
        precio_col_index = headers.index('PRECIO POR METRO CUADRADO') + 1
        ColorCodeLogic.color_code_prices_with_shades(ws, precio_col_index)
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="search_results.xlsx"'
        wb.save(response)

        return response


