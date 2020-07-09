from django.shortcuts import render, redirect
from django.contrib import messages

from decouple import config
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .models import Contact

# Create your views here.
def contact(request):
  if request.method == 'POST':
    listing_id = request.POST['listing_id']
    listing = request.POST['listing']
    name = request.POST['name']
    email = request.POST['email']
    phone = request.POST['phone']
    message = request.POST['message']
    user_id = request.POST['user_id']
    realtor_email = request.POST['realtor_email']

    # Check if user has already made an inquiry
    if request.user.is_authenticated:
      user_id = request.user.id
      has_contacted = Contact.objects.all().filter(listing_id=listing_id, user_id=user_id)
      print(has_contacted)
      if has_contacted:
        messages.error(request, "You have already made an inquiry for this listing")
        return redirect('/listings/'+listing_id)

    #Send email
    # send_mail(
    #   'Property Listing Inquiery',
    #   'There has been an inquiery for ' + listing + '. Sign into the admin pannel for more info',
    #   'btremarcusmonterroso@gmail.com',
    #   [realtor_email, 'mmonterroso@gmail.com'],
    #   fail_silently=False
    # )

    #Set Email
    message = Mail(
      from_email=config('SENDGRID_EMAIL_USER'),
      to_emails=email, 
      subject='Property Listing Inquiery',
      html_content='<strong>There has been an inquiery for ' + listing + '. Sign into the admin pannel for more info</strong>'
    )

    #Send Email: 
    try: 
      sg = SendGridAPIClient(config('SENDGRID_API_KEY'))
      response = sg.send(message)
      print(response.status_code) 
      print(response.body)
      print(response.headers)

      #Save contact if email is successful
      contact = Contact(listing=listing, listing_id=listing_id, name=name,
        email=email, phone=phone, message=message, user_id=user_id)

      contact.save()
      
      messages.success(request, 'Your request has been submitted, a realtor will get back to you soon.')
    except Exception as e: 
      print(e)
      messages.error(request, 'Sorry, there was an error with your request, please try again.')

    return redirect('/listings/'+listing_id)