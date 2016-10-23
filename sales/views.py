from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .forms import *
from .models import *
from .constants import DEFAULT_PRICES


def overview(request):
    top_sellers = None
    return render(request, 'sales/overview.html')


def login_site(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['seller'] = request.user.id
                #######
                # Need to Update this
                #######
                request.session['campaign'] = 1

                return HttpResponseRedirect(reverse('sales:welcome'))
    return render(request, 'sales/login.html')


def logout_site(request):
    del request.session['seller']
    del request.session['campaign']
    logout(request)
    return HttpResponseRedirect(reverse('sales:login_site'))


def require_login(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('sales:login_site'))


##################
# helper fn
##################
def ticket_is_already_sold(ticket_number):
    if Tickets.objects.filter(tick_id=ticket_number).exists():
        return True
    else:
        return False

def ticket_info(request):
    require_login(request)
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
    context = {'price1': prices['price1'],
               'price3': prices['price3'],
               'price10': prices['price10']}
    if request.method == 'POST':
        ticket_prices = {}
        tickets = {}
        for key in request.POST:
            if key[:8] == 'selector':
                ticket_prices[key[8:]] = request.POST[key]
            elif key[:6] == 'ticket':
                tickets[key[6:]] = request.POST[key]
        new_tickets = []
        total_price = 0
        repeated_ticket_numbers = []
        for key in tickets:
            if ticket_is_already_sold(tickets[key]):
                # add erroneous ticket to list of bad numbers
                repeated_ticket_numbers.append(tickets[key])

            price_lookup = ticket_prices[key[:len(key)-2]]
            if str(price_lookup) in ['1', '2']:
                new_tickets.append(Tickets(
                    tick_id = str(tickets[key]),
                    sale_date = timezone.now(),
                    tick_type = price_lookup,
                    buyer_id = Buyer.objects.get(pk=request.session['buyer']),
                    seller_id = request.user,
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
                        seller_id = request.user,
                        camp_id = Campaign.objects.get(pk=request.session['campaign'])
                    ))
                total_price += prices['price10']
        # Fail if user enters previously sold tickets
        if len(repeated_ticket_numbers) > 0:
            bad_tix = ' '.join(x for x in repeated_ticket_numbers)
            error_message = "The following tickets have already been sold. " + \
                            ', '.join(x for x in repeated_ticket_numbers) + \
                            "\nPlease check your entry"
            context['multi_key_error'] = error_message
            return render(request, 'sales/ticket_info.html', context)

        # Else, tickets are good so commit to d/b
        for ticket in new_tickets:
            ticket.save()
        request.session['total_price'] = str(total_price)
        return HttpResponseRedirect(reverse('sales:thankyou'))

    return render(request, 'sales/ticket_info.html', context)


def check_email(request):
    require_login(request)
    if request.method == 'POST':
        form = EmailCheckForm(request.POST)
        if form.is_valid():
            if Buyer.objects.filter(email=request.POST['email']).exists():
                request.session['buyer'] = \
                    Buyer.objects.get(email=request.POST['email']).id
            else:
                request.session['buyer'] = None
                request.session['email'] = request.POST['email']
        return HttpResponseRedirect(reverse('sales:client_info'))

    context = {'email_form': EmailCheckForm}
    return render(request, 'sales/email.html', context)


def client_info(request):
    require_login(request)
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
    if request.session['buyer'] is not None:
        buyer_form = DonorInputForm(
            instance=Buyer.objects.get(pk=request.session['buyer'])
        )
        customer_message = "Thank you for purchaing another ticket.\n " \
                           "Please check your contact information below."
    else:
        buyer_form = DonorInputForm(
            initial={'email': request.session['email']}
        )
        customer_message = "Please fill in your contact information."
    context = {
        'buyer_form': buyer_form,
        'customer_message': customer_message,
    }
    return render(request, 'sales/client_info.html', context)


def thankyou(request):
    require_login(request)
    if request.method == 'POST':
        del request.session['buyer']
        del request.session['total_price']
        return HttpResponseRedirect(reverse('sales:welcome'))
    context = {
        'ticket_cost': request.session['total_price']
    }
    return render(request, 'sales/thankyou.html', context)


def welcome(request):
    require_login(request)
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

    if request.method == 'POST':
        return HttpResponseRedirect(reverse('sales:email'))
    seller = User.objects.get(pk=request.session['seller'])
    tickets_sold = Tickets.objects.filter(seller_id_id=request.session['seller']).count()

    money_sold_singles = Tickets.objects.filter(
        seller_id_id=request.session['seller'],
        tick_type=1,
        camp_id_id=request.session['campaign']
    ).count() * Campaign.objects.get(pk=request.session['campaign']).tick_price1
    money_sold_triples = Tickets.objects.filter(
        seller_id_id=request.session['seller'],
        tick_type=2,
        camp_id_id=request.session['campaign']
    ).count() * Campaign.objects.get(pk=request.session['campaign']).tick_price3 / 3
    money_sold_tens = Tickets.objects.filter(
        seller_id_id=request.session['seller'],
        tick_type=3,
        camp_id_id=request.session['campaign']
    ).count() * Campaign.objects.get(pk=request.session['campaign']).tick_price10 / 10

    total_sold_singles = Tickets.objects.filter(
        tick_type=1,
        camp_id_id=request.session['campaign']
    ).count() * Campaign.objects.get(pk=request.session['campaign']).tick_price1
    total_sold_triples = Tickets.objects.filter(
        tick_type=2,
        camp_id_id=request.session['campaign']
    ).count() * Campaign.objects.get(pk=request.session['campaign']).tick_price3 / 3
    total_sold_tens = Tickets.objects.filter(
        tick_type=3,
        camp_id_id=request.session['campaign']
    ).count() * Campaign.objects.get(pk=request.session['campaign']).tick_price10 / 10
    total_raised = total_sold_singles + total_sold_triples + total_sold_tens


    campaign_goal = Campaign.objects.get(pk=request.session['campaign']).fund_goal
    therm_url = 'http://www.coolfundraisingideas.net/thermometer/thermometer.php?currency=dollar&goal=' + \
        str(campaign_goal) + '&current=' + str(total_raised) + \
        '&color=green&size=large'
    context = {
        'seller_name': seller.first_name,
        'tickets_sold': tickets_sold,
        'money_sold': money_sold_singles + money_sold_triples + money_sold_tens,
        'campaign_goal': "{:,}".format(campaign_goal),
        'image_src': therm_url,
    }
    return render(request, 'sales/welcome.html', context)
