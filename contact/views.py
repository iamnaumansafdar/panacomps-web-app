import random
import base64
import openai 
from django.views.generic.edit import FormView
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from .models import ContactSupport, GlossaryTerm
from .forms import ContactSupportForm
from django.views.generic import ListView
from datetime import datetime, timedelta, timezone
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AIPromptTemplate
from .langchain import send_to_ai
from django.template import Template, Context
from panaEstate.models import Metrics
from django.core.mail import EmailMessage


# class ContactSupportView(FormView):
#     template_name = 'support/contact_form.html'
#     form_class = ContactSupportForm
#     success_url = reverse_lazy('support_confirmation')

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user'] = self.request.user
#         return kwargs

#     def form_valid(self, form):
#         # Generate a random 8-digit ticket number
#         ticket_number = str(random.randint(10000000, 99999999))

#         # Save form data to the model
#         contact = form.save(commit=False)
#         contact.ticket_number = ticket_number
#         contact.attachment = self.request.FILES.get('attachment')
#         contact.save()

#         # Send email notification
#         send_mail(
#             f'Technical Support Request - Ticket #{ticket_number}',
#             f'Full Name: {contact.user_name}\nEmail: {contact.user_email}\nCategory: {contact.category}\nSubject: {contact.subject}\nDetails: {contact.details}\nTicket Number: {ticket_number}',
#             settings.DEFAULT_FROM_EMAIL,
#             ['info@panacomps.com'],
#         )

#         return super().form_valid(form)


class ContactSupportView(FormView):
    template_name = 'support/contact_form.html'
    form_class = ContactSupportForm
    success_url = reverse_lazy('support_confirmation')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_invalid(self, form):
        print(form.errors)  # Debugging: Print form errors to console
        return super().form_invalid(form)

    def form_valid(self, form):
        # Generate a random 8-digit ticket number
        ticket_number = str(random.randint(10000000, 99999999))

        # Save form data to the model
        contact = form.save(commit=False)
        contact.ticket_number = ticket_number
        contact.attachment = self.request.FILES.get('attachment')
        contact.save()

        # Prepare email content
        email_subject = f'Technical Support Request - Ticket #{ticket_number}'
        email_body = (
            f'Full Name: {contact.user_name}\n'
            f'Email: {contact.user_email}\n'
            f'Category: {contact.category}\n'
            f'Subject: {contact.subject}\n'
            f'Details: {contact.details}\n'
            f'Ticket Number: {ticket_number}'
        )

        # Create email
        email = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            # to=['raorehmat11@gmail.com'],
            to=['info@panacomps.com'],
        )

        # Attach file if present
        attachment = self.request.FILES.get('attachment')
        if attachment:
            print(f"File name: {attachment.name}")
            print(f"File size: {attachment.size}")
            print(f"File content type: {attachment.content_type}")

            if attachment.content_type == 'text/csv':
                attachment_file = attachment.read()
                print(f"Type of attachment_file: {type(attachment_file)}")
                email.attach(attachment.name, attachment_file, attachment.content_type)
            else:
                attachment.seek(0) 
                email.attach(attachment.name, attachment.read(), attachment.content_type)


        # Send email
        email.send()
        # try:
        #     email.send()
        # except Exception as e:
        #     print(f"Error sending email: {e}")
            # Handle error or notify user

        return super().form_valid(form)
    

                            # Encode attachment for SendGrid
            # base64_attachment = base64.b64encode(attachment_file).decode('utf-8')
            # email.attach(attachment.name, base64_attachment, attachment.content_type)



            # attachment_file = attachment.read()
            # if isinstance(attachment_file, str):
            #     # Convert string to bytes
            #     attachment_file = attachment_file.encode()

            # email.attach(attachment.name, attachment_file, attachment.content_type)



            # attachment.seek(0) 
            # email.attach(attachment.name, attachment.read(), attachment.content_type)
            # attachment.seek(0) 
            # email.attach(attachment.name, attachment.read(), attachment.content_type)




@csrf_exempt
def ai_analysis(request, template_id):
    if request.method == 'POST':
        template = AIPromptTemplate.objects.get(id=template_id)
        query_params = request.POST
        building = query_params.getlist("building")
        date_range = query_params.getlist("date_range")
        if date_range:
            date_range = date_range[0]  
        else:
            date_range = ""

        data = get_filtered_data(building, date_range)
        filled_prompt = fill_template_with_data(template.prompt_template, data)

         # Send the filled prompt to the AI (e.g., OpenAI)
        ai_response = send_to_ai(filled_prompt)
        print(ai_response, 'ai_response')

        # Return the AI result as JSON
        return JsonResponse({'result': ai_response})

    return JsonResponse({'error': 'Invalid request'}, status=400)



def get_filtered_data(building, date_range):
    queryset = Metrics.objects.all()

    if building:
            building = building[0] if building else ""
            queryset = queryset.filter(Q(edificio__icontains=building.strip()))


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
                Q(sales_transaction_date__isnull=True, edificio__icontains=building)
                )
            

    # Example of structuring the data based on your template
    data = {
            "filteredBuildings": {
                "data": {
                    "edificio": queryset.first().building.name if queryset.exists() else "",
                    "domicilio": list(queryset.values_list("domicilio", flat=True)[:10]),
                    "valor_del_traspaso": list(queryset.values_list("valor_del_traspaso", flat=True)),
                    "sales_transaction_date": list(queryset.values_list("sales_transaction_date", flat=True)),
                    "superficie_inicial": list(queryset.values_list("superficie_inicial", flat=True)),
                    "propietarios": list(queryset.values_list("propietarios", flat=True)),
                    "hipoteca": list(queryset.values_list("hipoteca", flat=True)),
                    "monto": list(queryset.values_list("monto", flat=True)),
                }
            },
            "salesDateRange": {
                "value": {
                    "start": start_date,
                    "end": end_date
                }
            }
        }

        

    return data


def fill_template_with_data(template_str, data):
    """
    Fill the prompt template with actual data.
    
    :param template_str: The template string with placeholders.
    :param data: Dictionary containing the data to replace placeholders.
    :return: A filled template with actual data.
    """
    template = Template(template_str)
    context = Context(data)  # Wrap the data dictionary in a Context object
    filled_prompt = template.render(context)
    return filled_prompt

