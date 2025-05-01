from django.test import TestCase
import os
import shutil
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment
from copy import copy
import statistics
from openpyxl.styles import Font, PatternFill
from openpyxl.drawing.image import Image
from datetime import datetime
from operator import itemgetter
from openpyxl.styles import Font
import urllib.parse
import unicodedata
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side


def format_folio_sheet(sheet, workbook, por_edificio, folio_folder_full_path):

    # comps_sheet = workbook[f"{por_edificio} Comps"]

    # Retrieve the renamed comps sheet, ensuring the name is within the character limit
    comps_sheet_name = f"{por_edificio} Comps"[:31]
    comps_sheet = workbook[comps_sheet_name]

    # Delete the second column "EDIFICIO"
    sheet.delete_cols(2)

    # Locate and rename "Sales Transaction Date" column to "Sales Date"
    for col_idx, col in enumerate(sheet.iter_cols(min_row=1, max_row=1, values_only=True)):
        if col[0] == "Sales Transaction Date":
            # Column indices are 1-based in openpyxl, so add 1 to the zero-based loop counter
            sheet.cell(row=1, column=col_idx + 1).value = "FECHA DE VENTA"
            break  # No need to continue the loop after finding and renaming the column

    # Function to find the row number of a FOLIO in the comps sheet
    def find_folio_row(folio, comps_sheet):
        for row_num, row in enumerate(comps_sheet.iter_rows(min_row=2, max_col=1, values_only=True), start=2):
            if str(row[0]).strip() == str(folio).strip():
                return row_num
        return None

    # Locate the columns for "Filename" and "PDF Text"
    filename_col_index = None
    pdf_text_col_index = None
    folio_col_index = None
    for col_idx, col in enumerate(sheet.iter_cols(min_row=1, max_row=1, values_only=True)):
        if col[0] == "Filename":
            filename_col_index = col_idx + 1
        if col[0] == "FOLIO":
            folio_col_index = col_idx + 1
        elif col[0] == "PDF Text":
            pdf_text_col_index = col_idx + 1

    # Set font, alignment, fill, and border for the entire sheet
    for col in sheet.columns:
        for cell in col:
            cell.font = Font(name="Helvetica Neue", size=18)
            # Default alignment
            cell.alignment = Alignment(horizontal="center", vertical="center")
            if cell.column == 1 and cell.row > 1:  # Assuming "FOLIO" is the first column
                cell.font = Font(name="Helvetica Neue", size=18, bold=True)
                folio_value = cell.value
                folio_row = find_folio_row(folio_value, comps_sheet)
                if folio_row:
                    cell.hyperlink = f"#'{comps_sheet_name}'!A{folio_row}"
                    # Preserve existing font properties and only change color and underline
                    cell.font = Font(name=cell.font.name, size=cell.font.size, bold=cell.font.bold,
                                     italic=cell.font.italic, underline='single', color='0563C1')

            # Specific alignments for "Filename" and "PDF Text" columns
            if cell.column == filename_col_index and cell.row != 1:
                cell.alignment = Alignment(
                    horizontal="left", vertical="center")
            elif cell.column == pdf_text_col_index:
                if cell.row != 1:
                    cell.alignment = Alignment(
                        horizontal="left", vertical="center", wrap_text=True)
                else:
                    cell.alignment = Alignment(
                        horizontal="center", vertical="center")

    # Formatting for the first row (header)
    for cell in sheet[1]:
        cell.font = Font(name="Helvetica Neue", size=18, bold=True)
        cell.fill = PatternFill(start_color="E5EAF4",
                                end_color="E5EAF4", fill_type="solid")

    # Formatting for the rows after the header
    row_fill = PatternFill(start_color="F7F4F4",
                           end_color="F7F4F4", fill_type="solid")
    thin_border = Border(left=Side(style='thin'), right=Side(
        style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.fill = row_fill
            cell.border = thin_border

        # # Get the absolute directory of the Excel file
    # excel_directory = os.path.dirname(os.path.abspath(__file__))

    # # Check if the filename and folio column indexes are provided
    # if filename_col_index and folio_col_index:
    #     # Iterate over each row in the sheet, starting from the second row to skip the header
    #     for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row):
    #         # Get the cell corresponding to the folio number and filename in the current row
    #         folio_cell = row[folio_col_index - 1]
    #         filename_cell = row[filename_col_index - 1]

    #         # Ensure that both folio and filename cells have values before proceeding
    #         if filename_cell.value and folio_cell.value:
    #             # Normalize the filename to NFC form to ensure consistent character representation
    #             normalized_filename = unicodedata.normalize('NFC', filename_cell.value)

    #             # URL-encode the filename to handle special characters, preserving slashes and parentheses
    #             encoded_filename = urllib.parse.quote(normalized_filename, safe="/()")

    #             # Construct the full absolute file path, appending the file:// protocol and organizing by folio
    #             absolute_file_path = os.path.join(excel_directory, "Folio_PDFs", str(folio_cell.value), encoded_filename)
    #             absolute_file_path = f"file:///{urllib.parse.quote(absolute_file_path)}"

    #             # Set the hyperlink for the filename cell to the absolute path of the corresponding file
    #             filename_cell.hyperlink = absolute_file_path

    #             # Set the font properties for the hyperlink, maintaining existing font properties and adding color and underline
    #             filename_cell.font = Font(name=filename_cell.font.name, size=filename_cell.font.size,
    #                                       bold=filename_cell.font.bold, italic=filename_cell.font.italic, underline='single', color='0563C1')

    # Calculate column widths
    calculate_column_widths(sheet)


def parse_date_string(date_str):
    try:
        return datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError:
        # If there's an error in conversion, return None
        return None


def sort_by_date(sheet, date_col_index):
    data_rows = [
        [cell.value for cell in row]
        for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row)
    ]

    # Parse the date strings into datetime objects for sorting
    for row in data_rows:
        date_str = row[date_col_index - 1]
        # Use the earliest representable date
        row[date_col_index - 1] = parse_date_string(date_str) or datetime.min

    # Sort the rows by the date column in descending order (most recent first)
    data_rows.sort(key=lambda r: (
        r[date_col_index - 1] is not None, r[date_col_index - 1]), reverse=True)

    # Write the sorted rows back into the worksheet, starting from row 2
    for row_idx, row in enumerate(data_rows, start=2):
        for col_idx, value in enumerate(row, start=1):
            cell = sheet.cell(row=row_idx, column=col_idx)
            # Check if the date is the minimum date, and replace it with "NO DATE"
            if isinstance(value, datetime) and value == datetime.min:
                cell.value = "NO DATE"
            else:
                cell.value = value if not isinstance(
                    value, datetime) else value.strftime("%d/%m/%Y")


def calculate_and_insert_average_sales_price(sheet, valor_col_index, metros_col_index):
    total_price = 0
    total_metros = 0

    for row in sheet.iter_rows(min_row=2, min_col=1, max_col=sheet.max_column):
        valor = convert_price_to_number(row[valor_col_index - 1].value)
        metros = convert_price_to_number(row[metros_col_index - 1].value)

        # Debugging: Print original and converted values for 'METROS CUADRADOS'
        #print(f"Row {row[0].row}, Original 'METROS CUADRADOS': '{row[metros_col_index - 1].value}', Converted 'METROS CUADRADOS': {metros}")

        if valor and metros:
            total_price += valor
            total_metros += metros

    # Avoid division by zero
    average_price = total_price / total_metros if total_metros > 0 else 0

    # More debugging: Print total price and total meters
    print(f"Total Price: {total_price}, Total Metros: {total_metros}")

    # Format the average price
    formatted_average_price = f"B/. {average_price:.2f}"

    # Add the average price to the spreadsheet
    last_row = sheet.max_row

    # Setting the label in Panamanian Spanish and English
    spanish_label = "Precio Promedio Ponderado de Venta por Metro Cuadrado"
    english_label = "(Weighted Average Sales Price per Square Meter)"

    average_label_cell_spanish = sheet.cell(row=last_row + 2, column=valor_col_index)  # Changed from metros_col_index
    average_value_cell = sheet.cell(row=last_row + 2, column=valor_col_index + 1)  # Keep this adjacent or as needed
    average_label_cell_english = sheet.cell(row=last_row + 3, column=valor_col_index)  # Changed from metros_col_index

    average_label_cell_spanish.value = spanish_label
    average_label_cell_english.value = english_label
    average_value_cell.value = formatted_average_price

    # Right align the label, center align the value, and make the Spanish label bold
    average_label_cell_spanish.alignment = Alignment(horizontal='right')
    average_label_cell_english.alignment = Alignment(horizontal='right')
    average_value_cell.alignment = Alignment(horizontal='center')
    average_label_cell_spanish.font = Font(
        name="Helvetica Neue", size=18, bold=True)
    average_label_cell_english.font = Font(name="Helvetica Neue", size=18)
    average_value_cell.font = Font(name="Helvetica Neue", size=18)

    # Add a border around the average value cell
    thin_border = Border(left=Side(style='thin'),
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))
    average_value_cell.border = thin_border

def trim_domicilio_values(sheet, domicilio_col_index):
    """
    Trims the values in the 'DOMICILIO' column to only include information up to 'EDIFICIO'.
    If 'EDIFICIO' is not found, the value is left as-is.
    """
    for row in sheet.iter_rows(min_row=2, min_col=domicilio_col_index, max_col=domicilio_col_index):
        cell = row[0]  # Get the first (and only) cell in the tuple
        value = cell.value
        if value and 'EDIFICIO' in value:
            # Trim the value up to the word 'EDIFICIO', excluding it
            trimmed_value = value.split('EDIFICIO')[0].rstrip(', ')
            cell.value = trimmed_value

# Function to find column index by header name


def find_column_index(sheet, header_name):
    for col_idx, col in enumerate(sheet.iter_cols(min_row=1, max_row=1, values_only=True)):
        #print(col)  # Debug: Print each column's header
        if col[0] == header_name:  # Access the first element of the tuple directly
            return col_idx + 1  # Adding 1 because Excel columns start at 1
    return None

# Function to convert price string to a float, handling both prices and square meters

# Rearrange the columns in the metrics sheet according to the desired order


def rearrange_columns(metrics_sheet, desired_order):
    # Create a mapping of current column data
    current_data = {}
    for col_name in desired_order:
        col_idx = find_column_index(metrics_sheet, col_name)
        if col_idx is not None:  # If column was found
            # Store the entire column data by column name
            current_data[col_name] = [metrics_sheet.cell(row=i, column=col_idx).value
                                      for i in range(1, metrics_sheet.max_row + 1)]

    # Clear current sheet data to prevent overwriting issues
    for row in metrics_sheet.iter_rows(min_row=1, max_row=metrics_sheet.max_row, min_col=1, max_col=metrics_sheet.max_column):
        for cell in row:
            cell.value = None  # Clear the cell value

    # Apply the stored data into the new column structure
    for new_idx, col_name in enumerate(desired_order, start=1):
        if col_name in current_data:  # Check if we have stored data for this column
            for row_idx, value in enumerate(current_data[col_name], start=1):
                # Reapply the stored data
                metrics_sheet.cell(row=row_idx, column=new_idx).value = value

# Continue with the rest of your formatting and operations

def convert_price_to_number(value):
    if isinstance(value, str):
        # For 'METROS CUADRADOS' values with 'm²' (with or without spaces)
        if 'm²' in value:
            try:
                # Remove spaces and extract the numeric part before 'm²'
                numeric_part = value.replace(' ', '').split('m²')[0]
                return float(numeric_part)
            except ValueError:
                return None  # Return None if conversion fails

        # For 'VALOR DEL TRASPASO' values (e.g., "B/.1,312,000.00")
        if value.startswith('B/.'):
            value = value.replace('B/.', '').replace(',', '').strip()
            try:
                return float(value)
            except ValueError:
                return None

        # For simple decimal number values, typical in 'METROS CUADRADOS'
        try:
            return float(value)
        except ValueError:
            return None  # Return None if conversion fails

        if value.upper() == 'NO DATA':
            return None

        elif isinstance(value, (int, float)):
            return value

        return None


def color_code_prices_with_shades(sheet, price_col_index):
    prices = []
    for row in sheet.iter_rows(min_row=2, min_col=price_col_index, max_col=price_col_index):
        cell = row[0]
        price = convert_price_to_number(cell.value)
        if price is not None:
            prices.append(price)

    if not prices:
        print("No valid prices found.")
        return

    mean_price = statistics.mean(prices)
    std_dev_price = statistics.stdev(prices) if len(prices) > 1 else 0

    print(f"Mean Price: {mean_price}, Standard Deviation: {std_dev_price}")

    for row in sheet.iter_rows(min_row=2, min_col=price_col_index, max_col=price_col_index):
        cell = row[0]
        price = convert_price_to_number(cell.value)

        # Debugging: Print original and converted values
        #print(
         #   f"Row {cell.row}, Original Value: '{cell.value}', Converted Price: {price}")

        if price is None:
            color = "D3D3D3"  # Light Gray for "NO DATA"
        else:
            deviation = (price - mean_price) / \
                std_dev_price if std_dev_price != 0 else 0
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

        cell.fill = PatternFill(
            start_color=color, end_color=color, fill_type="solid")
        cell.font = Font(name=cell.font.name, size=cell.font.size,
                         bold=cell.font.bold, italic=cell.font.italic, color="000000")


def copy_sheet(source_sheet, target_workbook):
    # Create a new worksheet in the target workbook with the same title as the source sheet
    target_sheet = target_workbook.create_sheet(title=source_sheet.title)

    for row in source_sheet.iter_rows():
        for cell in row:
            new_cell = target_sheet.cell(
                row=cell.row, column=cell.column, value=cell.value)
            # Copy style if needed
            if cell.has_style:
                new_cell.font = copy(cell.font)
                new_cell.border = copy(cell.border)
                new_cell.fill = copy(cell.fill)
                new_cell.number_format = copy(cell.number_format)
                new_cell.protection = copy(cell.protection)
            # Set alignment to center and middle
            new_cell.alignment = Alignment(
                horizontal='center', vertical='center', wrap_text=True)

    # Set the width of the first column to 25
    target_sheet.column_dimensions[get_column_letter(1)].width = 25

    # Set a default column width of 100 for all other columns
    default_width = 75
    for col in target_sheet.columns:
        if col[0].column != 1:  # Skip the first column
            target_sheet.column_dimensions[get_column_letter(
                col[0].column)].width = default_width

     # Set a default column width of 100 characters for all columns except the first
    default_width = 100
    for col in target_sheet.columns:
        if col[0].column != 1:  # Skip the first column
            target_sheet.column_dimensions[get_column_letter(
                col[0].column)].width = default_width

    return target_sheet


def calculate_column_widths(metrics_sheet):
    for col_idx, col in enumerate(metrics_sheet.iter_cols(min_col=1, max_col=metrics_sheet.max_column), start=1):
        max_length = 0
        column_letter = get_column_letter(col_idx)
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass

        # Adjust the column width
        metrics_sheet.column_dimensions[column_letter].width = (
            max_length + 2) * 2.0  # Adjust the multiplier as needed


def create_panacomps_excel():
    # Determine the directory where this script is located
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to searchCriteria.txt based on the script's location
    search_criteria_path = os.path.join(script_directory, 'searchCriteria.txt')

    # Read the searchCriteria file and extract the value for "Por Edificio:"
    por_edificio = ''
    with open(search_criteria_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "Por Edificio:" in line:
                por_edificio = line.split(":")[1].strip()

    if not por_edificio:
        raise ValueError("Por Edificio value not found in searchCriteria.txt")

    print(f"Running script for por_edificio: {por_edificio}")

    # Define various paths
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    folios_dir = os.path.join(downloads_dir, "Folios")
    top_level_path = os.path.join(folios_dir, por_edificio)
    folio_folder_full_path = os.path.join(top_level_path, "Folio_PDFs")
    panacomps_output_folder = os.path.join(
        folio_folder_full_path, 'Panacomps Output')
    # Define the path for the Panacomps Digital Asset Template folder
    panacomps_template_folder = os.path.join(
        script_directory, "Panacomps Digital Asset Template")

    # Check if panacomps_output_path exists, if not, create it
    if not os.path.exists(panacomps_output_folder):
        os.makedirs(panacomps_output_folder)

    # Define source and output Excel file paths
    source_excel_path = os.path.join(
        folio_folder_full_path, 'PDF_Folios_Extraction.xlsx')
    new_excel_path = os.path.join(
        panacomps_output_folder, f"Panacomps {por_edificio}.xlsx")

    # Copy the source Excel file to the new file
    shutil.copyfile(source_excel_path, new_excel_path)

    # Load the new Excel workbook
    workbook = load_workbook(new_excel_path)

   # Define sheets to be removed
    sheets_to_remove = ["Folios", "Database Imports", "Panacomps Output"]


    # Define the Metrics sheet. This assumes the Metrics sheet is named 'Metrics'
    # Adjust the sheet name if necessary
    metrics_sheet = workbook.get_sheet_by_name(
        'Metrics')  # Use your actual Metrics sheet name

    # Output all headers from the first row of the 'Metrics' sheet
    # Before removing sheets, just after loading the workbook
    if metrics_sheet:  # Check if the metrics_sheet is correctly defined
        # Row 1 for headers
        metrics_headers = [cell.value for cell in metrics_sheet[1]]
        #print("Initial headers in 'Metrics' sheet right after loading workbook:", metrics_headers)
    else:
        print("Metrics sheet not found in the workbook")
    
    # Remove specified sheets if they exist
    for sheet_name in sheets_to_remove:
        if sheet_name in workbook.sheetnames:
            del workbook[sheet_name]

    # Define the path for the image
    image_path = os.path.join(
        panacomps_template_folder, "Panacomps Banner.png")

    # Load and copy the 'Panacomps' worksheet
    panacomps_banner_path = os.path.join(
        panacomps_template_folder, "Panacomps Banner.xlsx")
    panacomps_banner_workbook = load_workbook(panacomps_banner_path)
    panacomps_com_sheet = panacomps_banner_workbook["Panacomps"]
    copied_panacomps_com_sheet = copy_sheet(panacomps_com_sheet, workbook)
    copied_panacomps_com_sheet.title = "Panacomps"

    # Add the image to the copied 'Panacomps' sheet
    img = Image(image_path)

    # Adjust 'A1' to the cell where you want the image
    copied_panacomps_com_sheet.add_image(img, 'A1')

    # Define fill color for 'Panacomps' sheet and no border
    panacomps_fill = PatternFill(
        start_color="25336F", end_color="25336F", fill_type="solid")
    no_border = Border()

    # Apply fill color and no border to each cell up to the 100th row in 'Panacomps' sheet
    # Iterate through rows 1 to 100 and columns 1 to 52 (Column AZ)
    for row in range(1, 101):
        for col in range(1, 53):
            cell = copied_panacomps_com_sheet.cell(row=row, column=col)
            cell.fill = panacomps_fill
            cell.border = no_border

    # Formatting the "Metrics" sheet
    metrics_sheet = workbook["Metrics"]

    # Insert a new column at the beginning
    metrics_sheet.insert_cols(1)

    # Set the header for the new column
    metrics_sheet.cell(row=1, column=1, value="COMP #")

    # Populate the new column with incremental numbers based on 'FOLIO' column presence
    folio_column = 2  # Assuming 'FOLIO' is now the second column after insertion
    comp_number = 1
    for row in range(2, metrics_sheet.max_row + 1):  # Start from row 2
        if metrics_sheet.cell(row=row, column=folio_column).value is not None:
            metrics_sheet.cell(row=row, column=1, value=comp_number)
            comp_number += 1

   # Rename columns first
    for cell in metrics_sheet[1]:  # First row is header
        if cell.value == "Sales Transaction Date":
            cell.value = "FECHA DE VENTA"
        elif cell.value == "Price per square meter":
            cell.value = "PRECIO POR METRO CUADRADO"
        elif cell.value == "TIMESTAMP":
            cell.value = "MARCA DE TIEMPO"
        elif cell.value == "SUPERFICIE INICIAL":
            cell.value = "METROS CUADRADOS"

    # Define a dictionary for column actions: True for delete, False for keep
    column_actions = {
        "COMP #": True,
        "FOLIO": False,
        "CODIGO UBICACIÓN": True,
        "MUNICIPIO": True,
        "EDIFICIO": False,
        "FECHA DE CONSTRUCCIÓN": True,
        "FECHA DE OCUPACIÓN": True,
        "PROPIETARIOS": False,
        "USO DEL SUELO": False,
        "DOMICILIO": False,
        "FECHA DE VENTA": False,
        "VALOR": False,
        "VALOR DEL TERRENO": False,
        "VALOR DE MEJORAS": False,
        "VALOR DEL TRASPASO": False,
        "METROS CUADRADOS": False,
        "PRECIO POR METRO CUADRADO": False,
        "HIPOTECA": False,
        "MONTO": False,
        "TASA EFECTIVA": False,
        "TASA NOMINAL": False,
        "INTERÉS ANUAL": False,
        "FECI": False,
        "INTERÉS ANUAL + FECI": False,
        "NOMBRE": False,
        "MARCA DE TIEMPO": False
        # Add other columns as needed
    }

    propietarios_col_index = find_column_index(
        metrics_sheet, "PROPIETARIOS")  # Finding index for "PROPIETARIOS"
    
    # Print out the value for debugging
    #print("AFTER TRUE/FALSE propietarios_col_index:", propietarios_col_index)

    # Function to delete or keep columns based on the column_actions dictionary
    def update_columns(sheet):
        columns_to_delete = []
        for col_num, col_cells in enumerate(sheet.iter_cols()):
            col_header = col_cells[0].value
            # Default to keep if not in dictionary
            if column_actions.get(col_header, False):
                # Column numbers are 1-indexed in openpyxl
                columns_to_delete.append(col_num + 1)

        # Delete columns in reverse order to avoid shifting indexes
        for col_num in reversed(columns_to_delete):
            sheet.delete_cols(col_num)

    # Call the function to update the 'metrics_sheet'
    update_columns(metrics_sheet)

    # Ensure the comps sheet title is within Excel's character limit
    comps_sheet_title = f"{por_edificio} Comps"[:31]

    # Rename the "Metrics" sheet with the truncated name
    metrics_sheet.title = comps_sheet_title

    # Load the 'Legend' worksheet from 'Legend.xlsx'
    legend_excel_path = os.path.join(panacomps_template_folder, "Legend.xlsx")
    legend_workbook = load_workbook(legend_excel_path)
    legend_sheet = legend_workbook["Legend"]

    # Use the copy_sheet function to copy the 'Legend' worksheet
    copied_legend_sheet = copy_sheet(legend_sheet, workbook)

    # Rename the copied sheet as needed, e.g., "Legend"
    copied_legend_sheet.title = "Legend"

    # Ensure 'Panacomps' sheet is the first sheet
    if "Panacomps" in workbook.sheetnames:
        panacomps_index = workbook.sheetnames.index("Panacomps")
        workbook.move_sheet("Panacomps", -panacomps_index)

    # Ensure '{por_edificio} Comps' is the second sheet
    # Truncate the name when renaming/creating the sheet
    # comps_sheet_title = f"{por_edificio} Comps"[:31]
    if comps_sheet_title in workbook.sheetnames:
        comps_index = workbook.sheetnames.index(comps_sheet_title)
        # Calculate the offset considering the new position of 'Panacomps'
        workbook.move_sheet(comps_sheet_title, 1 - comps_index)

    # Ensure 'Legend' is the third sheet
    if "Legend" in workbook.sheetnames:
        legend_index = workbook.sheetnames.index("Legend")
        # Calculate the offset considering the new positions of 'Panacomps' and '{por_edificio} Comps'
        workbook.move_sheet("Legend", 2 - legend_index)

    

    # START SORTING BY "FECHA DE VENTA"

    # Find the column index for "FECHA DE VENTA"
    fecha_venta_col_index = find_column_index(
        metrics_sheet, "FECHA DE VENTA")

    # Ensure the column index was found before attempting to sort
    if fecha_venta_col_index:
        sort_by_date(metrics_sheet, fecha_venta_col_index)
    else:
        print(f"Column 'FECHA DE VENTA' not found")

    # END SORTING BY "FECHA DE VENTA"

    # Determine the column for 'MARCA DE TIEMPO'
    marca_tiempo_col = None
    for idx, cell in enumerate(metrics_sheet[1], start=1):
        if cell.value == 'MARCA DE TIEMPO':
            marca_tiempo_col = idx
            break

    if marca_tiempo_col is None:
        raise ValueError("Column 'MARCA DE TIEMPO' not found")

    # Get the first value from 'MARCA DE TIEMPO' column as the password
    dynamic_password = metrics_sheet.cell(row=2, column=marca_tiempo_col).value
    if dynamic_password is None:
        raise ValueError(
            "No data found in 'MARCA DE TIEMPO' for password generation")

    # Convert the password to string format
    dynamic_password = str(dynamic_password)

    # Protect the copied 'Panacomps' sheet
    copied_panacomps_com_sheet.protection.sheet = True
    copied_panacomps_com_sheet.protection.password = dynamic_password

    # Protect the "Metrics" sheet
    metrics_sheet.protection.sheet = True
    metrics_sheet.protection.password = dynamic_password

    # Protect the copied 'Legend' sheet
    copied_legend_sheet.protection.sheet = True
    copied_legend_sheet.protection.password = dynamic_password

    # Protect all other sheets after "Legend"
    legend_found = False
    for sheet in workbook.worksheets:
        if sheet.title == "Legend":
            legend_found = True
            continue
        if legend_found:
            sheet.protection.sheet = True
            sheet.protection.password = dynamic_password

    # Make 'Panacomps' the active sheet
    workbook.active = workbook.index(copied_panacomps_com_sheet)

    ###################  FIRST WORKBOOK SAVED, NOW PERFORM FORMATTING  ###################
        
    # Save the updated workbook
    workbook.save(new_excel_path)

    # Define the new desired column order after updating
    desired_column_order = [
        "FOLIO",
        "EDIFICIO",
        "FECHA DE VENTA",
        "DOMICILIO",
        "METROS CUADRADOS",
        "VALOR DEL TRASPASO",
        "PRECIO POR METRO CUADRADO",
        "VALOR",
        "VALOR DEL TERRENO",
        "VALOR DE MEJORAS",
        "USO DEL SUELO",  # Add the new column here
        "PROPIETARIOS",
        "HIPOTECA",
        "MONTO",
        "TASA EFECTIVA",
        "TASA NOMINAL",
        "INTERÉS ANUAL",
        "FECI",
        "INTERÉS ANUAL + FECI",
        "NOMBRE",
        "MARCA DE TIEMPO"
    ]

    workbook = load_workbook(new_excel_path)

   # Save the updated workbook before rearranging
    workbook.save(new_excel_path)

    # Reload the workbook
    workbook = load_workbook(new_excel_path)
    # Revert to using the original variable name for the metrics sheet
    metrics_sheet = workbook[comps_sheet_title]  # Original reference restored

    propietarios_col_index = find_column_index(
        metrics_sheet, "PROPIETARIOS")  # Finding index for "PROPIETARIOS"
    
    # Call the rearrange function
    rearrange_columns(metrics_sheet, desired_column_order)

    propietarios_col_index = find_column_index(
            metrics_sheet, "PROPIETARIOS")  # Finding index for "PROPIETARIOS"
    
    # Print out the value for debugging
    #print("AFTER REARRANGE propietarios_col_index:", propietarios_col_index)
    
    # Find the column index for "DOMICILIO" etc.
    domicilio_col_index = find_column_index(metrics_sheet, "DOMICILIO")
    valor_col_index = find_column_index(metrics_sheet, "VALOR DEL TRASPASO")
    metros_col_index = find_column_index(metrics_sheet, "METROS CUADRADOS")
    precio_col_index = find_column_index(
        metrics_sheet, "PRECIO POR METRO CUADRADO")
    propietarios_col_index = find_column_index(
        metrics_sheet, "PROPIETARIOS")  # Finding index for "PROPIETARIOS"
    
    # Print out the value for debugging
    print("propietarios_col_index:", propietarios_col_index)

 # if valor_col_index and metros_col_index:
    #calculate_and_insert_average_sales_price(
     #   metrics_sheet, valor_col_index, metros_col_index, precio_col_index)

    # Set font for the entire sheet
    for col in metrics_sheet.columns:
        for cell in col:
            cell.font = Font(name="Helvetica Neue", size=18)
            cell.alignment = Alignment(horizontal="center")

    for cell in metrics_sheet[1]:  # First row is header
        cell.alignment = Alignment(horizontal="center")
        cell.font = Font(name="Helvetica Neue", size=18, bold=True)

    for cell in metrics_sheet['A']:  # First column is 'FOLIO'
        cell.font = Font(name="Helvetica Neue", size=18, bold=True)

    header_fill = PatternFill(start_color="E5EAF4",
                              end_color="E5EAF4", fill_type="solid")
    row_fill = PatternFill(start_color="F7F4F4",
                           end_color="F7F4F4", fill_type="solid")
    for cell in metrics_sheet[1]:  # First row is header
        cell.fill = header_fill
    for row in metrics_sheet.iter_rows(min_row=2):
        for cell in row:
            cell.fill = row_fill

    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                         top=Side(style='thin'), bottom=Side(style='thin'))
    for row in metrics_sheet.iter_rows():
        for cell in row:
            cell.border = thin_border

    # Apply the logic to trim values in the "DOMICILIO" column
    if domicilio_col_index:
        trim_domicilio_values(metrics_sheet, domicilio_col_index)

    # Left-align the "PROPIETARIOS" column, excluding the header
    if propietarios_col_index:
        for row in metrics_sheet.iter_rows(min_row=2, min_col=propietarios_col_index, max_col=propietarios_col_index):
            for cell in row:
                cell.alignment = Alignment(horizontal='left')

    precio_col_name = "PRECIO POR METRO CUADRADO"
    precio_col_index = find_column_index(metrics_sheet, precio_col_name)

    if precio_col_index is not None:
        # Apply color coding to "PRECIO POR METRO CUADRADO" column
        color_code_prices_with_shades(metrics_sheet, precio_col_index)
    else:
        print(f"Column '{precio_col_name}' not found")

    # Recalculate column widths after rearranging
    calculate_column_widths(metrics_sheet)
        
    # if valor_col_index and metros_col_index:
    calculate_and_insert_average_sales_price(
        metrics_sheet, valor_col_index, metros_col_index, precio_col_index)


    # Locate the 'FOLIO' column in the f"{por_edificio} Comps" worksheet
    comps_sheet = workbook[comps_sheet_title]
    folio_col_index = find_column_index(comps_sheet, "FOLIO")

    # Create hyperlinks for each 'FOLIO' cell to the corresponding worksheet
    if folio_col_index:
        for row in comps_sheet.iter_rows(min_row=2, min_col=folio_col_index, max_col=folio_col_index):
            cell = row[0]  # The cell in the 'FOLIO' column
            folio_value = str(cell.value).strip(
            ) if cell.value is not None else ''

            # Break the loop if folio_value is 'None' or an empty string
            if not folio_value:
                #print("Encountered an invalid FOLIO value; stopping hyperlink creation.")
                break  # Exit the loop on encountering the first invalid folio value

            # Proceed if folio_value is valid
            #print(f"Creating hyperlink for FOLIO: {folio_value}")
            if folio_value in workbook.sheetnames:
                cell.hyperlink = f"#{folio_value}!A1"
                cell.font = Font(name=cell.font.name, size=cell.font.size, bold=cell.font.bold,
                                 italic=cell.font.italic, underline='single', color='0563C1')
            else:
                print(f"No matching sheet for FOLIO: {folio_value}")
    
    # Iterate over each sheet in the workbook after the "Legend" sheet and format it
    legend_index = workbook.sheetnames.index("Legend")
    for sheet_name in workbook.sheetnames[legend_index + 1:]:
        # Pass truncated name
        format_folio_sheet(
            workbook[sheet_name], workbook, por_edificio, folio_folder_full_path)
            

    # Define translations and notes for headers
    header_notes = {
        "COMP #": "Número de Comparación - Un identificador único para cada propiedad comparable en el conjunto de datos.",
        "FOLIO": "Un folio en el contexto del Registro Público de Panamá es un identificador único asociado a cada propiedad registrada.",
        "EDIFICIO": "Esto se refiere al nombre real del edificio (P.H.) tal como está registrado en el Registro Público de Panamá.",
        "DOMICILIO": "El término domicilio, en referencia a un apartamento en el Registro Público de Panamá, se refiere al número de unidad/piso.",
        "FECHA DE VENTA": "La fecha oficialmente registrada cuando la propiedad fue legalmente transferida del vendedor al comprador.",
        "VALOR DEL TRASPASO": "El monto financiero oficialmente registrado por el cual se vendió la propiedad.",
        "METROS CUADRADOS": "El área total registrada de la propiedad medida en metros cuadrados.",
        "PRECIO POR METRO CUADRADO": "Esto se calcula dividiendo el precio total de la propiedad por su área en metros cuadrados.",
        "MARCA DE TIEMPO": "Esto se referiría a la fecha y hora en que la información fue descargada por Panacomps del Registro Público de Panamá.",
        "VALOR": "Valor - El valor monetario estimado o valorado de la propiedad.",
        "VALOR DEL TERRENO": "Valor del Terreno - El valor de la componente del terreno de la propiedad.",
        "VALOR DE MEJORAS": "Valor de Mejoras - El valor de las mejoras o construcciones añadidas a la propiedad.",
        "PROPIETARIOS": "Propietarios - Los nombres de los propietarios legales de la propiedad.",
        "HIPOTECA": "Hipoteca - Indica si la propiedad está bajo una hipoteca.",
        "MONTO": "Monto - El monto total involucrado en una transacción o hipoteca.",
        "TASA EFECTIVA": "Tasa Efectiva - La tasa de interés real aplicada a una hipoteca o préstamo.",
        "TASA NOMINAL": "Tasa Nominal - La tasa de interés nominal de un préstamo o hipoteca, sin tener en cuenta la capitalización.",
        "INTERÉS ANUAL": "Interés Anual - El monto total de interés que se acumula anualmente en un préstamo o hipoteca.",
        "FECI": "FECI - Un impuesto aplicado a las transacciones financieras.",
        "INTERÉS ANUAL + FECI": "Interés Anual + FECI - El total combinado de interés anual e impuesto FECI.",
        "NOMBRE": "Nombre - El nombre del individuo o entidad involucrado en la transacción de la propiedad."
    }

    # Assign comments based on renamed headers
    for cell in metrics_sheet[1]:  # Iterate again to assign comments
        cell.comment = Comment(header_notes.get(cell.value, ""), "Author")      

    # Save the workbook after rearranging the columns
    workbook.save(new_excel_path)

    print(f"Updated Excel file created at: {new_excel_path}")



if __name__ == "__main__":
    create_panacomps_excel()


