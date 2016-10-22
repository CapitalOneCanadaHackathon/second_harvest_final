from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
import datetime

from .forms import *
from .models import *
from .constants import DEFAULT_PRICES

# Create your views here.
def index(request):
    request.session['campaign'] = 1
    return render(request, 'sales/index.html')


##################
# helper fn
##################
def ticket_is_new(ticket_number):
    return True

def ticket_info(request):
    ##########
    # Delete when code is complete
    ##########
    if 'seller' not in request.session:
        request.session['seller'] = 1
    if 'buyer' not in request.session:
        request.session['buyer'] = 1
    if 'campaign' not in request.session:
        request.session['campaign'] = 1
    #############
    # end delete section
    #############
    curr_campaign = Campaign.objects.get(pk=request.session['campaign'])
    prices = {
        'price1': curr_campaign.tick_price1,
        'price3': curr_campaign.tick_price3,
        'price10': curr_campaign.tick_price10
    }

    if request.method == 'POST':
        ticket_prices = {}
        tickets = {}
        for key in request.POST:
            if key[:8] == 'selector':
                print('\n\n')
                print(request.POST[key])
                ticket_prices[key[8:]] = request.POST[key]
            elif key[:6] == 'ticket':
                tickets[key[6:]] = request.POST[key]
        new_tickets = []
        total_price = 0
        for key in tickets:
            if not ticket_is_new(tickets[key]):
                # raise error and return to ticket info page
                pass
            price_lookup = ticket_prices[key[:len(key)-2]]
            if str(price_lookup) in ['1', '2']:
                new_tickets.append(Tickets(
                    tick_id = str(tickets[key]),
                    sale_date = timezone.now(),
                    tick_type = price_lookup,
                    buyer_id = Buyer.objects.get(pk=request.session['buyer']),
                    seller_id = Seller.objects.get(pk=request.session['seller']),
                    camp_id = Campaign.objects.get(pk=request.session['campaign'])
                ))
                total_price += prices['price1'] if str(price_lookup) == '1' \
                    else prices['price3'] / 3
            else:
                for i in range(10):
                    new_tickets.append(Tickets(
                        tick_id = str(int(tickets[key]) + i),
                        sale_date = timezone.now(),
                        tick_type = price_lookup,
                        buyer_id = Buyer.objects.get(pk=request.session['buyer']),
                        seller_id = Seller.objects.get(pk=request.session['seller']),
                        camp_id = Campaign.objects.get(pk=request.session['campaign'])
                    ))
                total_price += prices['price10']
        for ticket in new_tickets:
            ticket.save()
        request.session['total_price'] = str(total_price)
        return HttpResponseRedirect(reverse('sales:thankyou'))

    context = {'price1': prices['price1'],
               'price3': prices['price3'],
               'price10': prices['price10']}
    return render(request, 'sales/ticket_info.html', context)


def client_info(request):
    if request.method == 'POST':
        form = DonorInputForm(request.POST)
        if form.is_valid():
            buyer = Buyer(
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                email=request.POST['email'],
                phone=request.POST['phone'],
                address=request.POST['address'],
                city=request.POST['city'],
                postal_code=request.POST['postal_code'],
                opt_out=True if 'opt_out' in request.POST else False,
            )
            buyer.save()
            request.session['buyer'] = buyer.id
        return HttpResponseRedirect(reverse('sales:ticket_info'))
    context = {
        'buyer_form': DonorInputForm
    }
    return render(request, 'sales/client_info.html', context)


def thankyou(request):
    if request.method == 'POST':
        del request.session['buyer']
        del request.session['total_price']
        return HttpResponseRedirect(reverse('sales:welcome'))
    context = {
        'ticket_cost': request.session['total_price']
    }
    return render(request, 'sales/thankyou.html', context)

#
# def total(data_file):
#     total_raised=0
#     with open(data_file, 'r') as data:
#         for i in data.readlines():
#             total_raised += float(i[:-2])
#     return total_raised


def welcome(request):
    ##########
    # Delete when code is complete
    ##########
    if 'seller' not in request.session:
        request.session['seller'] = 1
    if 'buyer' not in request.session:
        request.session['buyer'] = 1
    if 'campaign' not in request.session:
        request.session['campaign'] = 1
    #############
    # end delete section
    #############
    total_raised = '9000'
    therm_url = 'http://www.coolfundraisingideas.net/thermometer/thermometer.php?currency=dollar&goal=10000&current='+total_raised+'&color=green&size=large'
    context = {
        'seller_name': "Mary Smith",
        'image_src': therm_url
    }
    return render(request, 'sales/welcome.html', context)
