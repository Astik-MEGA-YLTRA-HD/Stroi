from django.shortcuts import render, redirect
from decimal import Decimal
from program.models import Orders, Day, Сonsumables

# Create your views here.
def index(request):
    orders = Orders.objects.all().order_by("-deadline")
    amount = 0
    for i in orders:
        amount+=i.amount
    
    remains = 0
    for i in orders:
        remains+=i.remains

    return render(request, 'program/index.html', {"orders":orders, "amount":amount, "remains":remains})

def add_order(request):

    try:
        if request.method == 'POST':
            title = request.POST["title"]
            address = request.POST["address"]
            amount = request.POST["amount"]
            deadline = request.POST["deadline"]

            if title!="" and address!="" and amount!="" and deadline!="":
                amount = Decimal(amount)
            
            Orders.objects.create(
                title=title,
                address=address,
                amount=amount,
                deadline=deadline,
                remains=amount,
            )
            return redirect('index')
    except:
        return redirect('index')

    return render(request, 'program/add_orders.html')

def day(request, _id):
    days = Day.objects.filter(order=_id).order_by("-date")
    amount = 0
    for i in days:
        amount+=i.amount

    return render(request, 'program/day.html', {"days":days, "amount":amount, "id":_id})

def add_day(request, _id):
    order = Orders.objects.get(pk=_id)
    if request.method == 'POST':
        date = request.POST["date"]

        if date!="":
            Day.objects.create(
                amount=Decimal(0),
                date=date,
                order=order,
            )
            return redirect('day', _id=_id)

    return render(request, 'program/add_day.html', {"id":_id})

def consumables(request, _id):

    day = Day.objects.get(pk=_id)
    print(day.order)

    consum = Сonsumables.objects.filter(day=_id)
    amount = 0
    for i in consum:
        amount+=i.prise

    print(consum)

    return render(request, 'program/consumables.html', {"consum":consum, "amount":amount, "id":_id, "order_id":day.order})

def add_consumables(request, _id):
    day = Day.objects.get(id=_id)

    if request.method == 'POST':
        title = request.POST["title"]
        count = request.POST["count"]
        prise = request.POST["prise"]

        if title!="" and prise!="":
            prise = Decimal(prise)

            consum = Сonsumables.objects.filter(day=_id)
            amount = Decimal(0)
            for i in consum:
                amount+=i.prise

        print(consum)

        Сonsumables.objects.create(
            title=title,
            count=count,
            amount=Decimal(prise)*Decimal(count),
            prise=prise,
            day=day,
        )

        Day.objects.filter(id=_id).update(
            amount=Decimal(day.amount)+Decimal(amount),
        )

        Orders.objects.filter(id=_id).update(
            remains=Decimal(day.amount)-Decimal(amount),
        )

        return redirect('consumables', _id=_id)

    return render(request, 'program/add_consumables.html', {"id":_id, "order_id":day.order})