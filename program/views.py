from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal
from program.models import Orders, Day, Сonsumables, Payment

# Функция индекса
def index(request):
    # Получаем все заказы, отсортированные по сроку сдачи (от ближайшего к дальнейшему)
    orders = Orders.objects.all().order_by('-deadline')

    # Рассчитываем общую сумму оплаченных денег и общий остаток по всем заказам
    amount_total = sum(order.amount for order in orders)
    remains_total = sum(order.remains for order in orders)

    # Передача контекста в шаблон
    context = {
        'orders': orders,              # Все заказы сразу передаются в шаблон
        'amount': f"{amount_total:,}",  # Форматированная сумма оплат
        'remains': f"{remains_total:,}"  # Форматированная сумма остатков
    }

    return render(request, 'program/index.html', context)


# Добавление заказа
def add_order(request):
    if request.method == 'POST':
        title = request.POST.get("title", "")
        address = request.POST.get("address", "")
        amount_str = request.POST.get("amount", "").strip()
        deadline = request.POST.get("deadline", "")
        
        if title and address and amount_str and deadline:
            try:
                amount = Decimal(amount_str)
                new_order = Orders.objects.create(
                    title=title,
                    address=address,
                    amount=amount,
                    deadline=deadline,
                    remains=amount
                )
                messages.success(request, f'Заказ "{new_order.title}" успешно добавлен.')
                return redirect('index')
            except Exception as e:
                messages.error(request, f'Ошибка при создании заказа: {e}')
        else:
            messages.warning(request, 'Все поля обязательны для заполнения!')
    return render(request, 'program/add_orders.html')


# Просмотр дней заказа
def day(request, _id):
    days = Day.objects.filter(order__pk=_id).order_by('-date').select_related()
    amount_total = sum(d.amount for d in days)

    # Добавляем предварительную подготовку данных для вывода суммы
    for day in days:
        day.total_consumables_amount = Decimal(sum(c.amount for c in Сonsumables.objects.filter(day=day))) + Decimal(sum(p.amount for p in Payment.objects.filter(day=day)))

    return render(request, 'program/day.html', {
        'days': days,
        'amount': amount_total,
        'id': _id
    })


# Добавление дня заказа
def add_day(request, _id):
    order = Orders.objects.get(pk=_id)
    if request.method == 'POST':
        date = request.POST.get("date", "")
        if date:
            try:
                new_day = Day.objects.create(amount=Decimal(0), date=date, order=order)
                messages.success(request, f'Новый день "{new_day.date}" успешно добавлен.')
                return redirect('day', _id=_id)
            except Exception as e:
                messages.error(request, f'Ошибка при создании дня: {e}')
        else:
            messages.warning(request, 'Поле "дата" обязательно для заполнения!')
    return render(request, 'program/add_day.html', {'id': _id})


# Просмотр расходных материалов
def consumables(request, _id):
    day = Day.objects.select_related('order').get(pk=_id)
    consum = Сonsumables.objects.filter(day=_id)
    paym = Payment.objects.filter(day=_id)
    amount_total_consum = sum(c.amount for c in consum)
    amount_total_paym = sum(p.amount for p in paym)
    return render(request, 'program/consumables.html', {
        'paym': paym,
        'consum': consum,
        'amount_consum': amount_total_consum,
        'amount_paym': amount_total_paym,
        'id': _id,
        'order_id': day.order.pk
    })


# Добавление расходных материалов
def add_consumables(request, _id):
    day = Day.objects.get(id=_id)
    if request.method == 'POST':
        title = request.POST.get("title", "")
        count_str = request.POST.get("count", "").strip()
        prise_str = request.POST.get("prise", "").strip()
        
        if title and prise_str:
            try:
                count = int(count_str)
                prise = Decimal(prise_str)
                
                # Создание нового расходного материала
                new_consumable = Сonsumables.objects.create(
                    title=title,
                    count=count,
                    prise=prise,
                    amount=Decimal(prise) * Decimal(count),
                    day=day
                )
                
                # Пересчёт суммы расходов за день
                updated_amount = sum(c.amount for c in Сonsumables.objects.filter(day=day))
                day.amount = updated_amount
                day.save()
                
                # Пересчёт общего баланса заказа
                order = day.order
                consumed_amount = sum(d.amount for d in Day.objects.filter(order=order))
                order.remains = order.amount - consumed_amount
                order.save()
                
                messages.success(request, f'Расходный материал "{new_consumable.title}" успешно добавлен.')
                return redirect('consumables', _id=_id)
            except Exception as e:
                messages.error(request, f'Ошибка при добавлении расходного материала: {e}')
        else:
            messages.warning(request, 'Необходимо заполнить все обязательные поля!')
    return render(request, 'program/add_consumables.html', {
        'id': _id,
        'order_id': day.order.pk
    })


# Добавление расходных материалов
def add_payment(request, _id):
    day = Day.objects.get(id=_id)
    if request.method == 'POST':
        name = request.POST.get("name")
        amount = request.POST.get("amount")
        
        if name and amount:

                # Создание нового расходного материала
                new_consumable = Payment.objects.create(
                    name=name,
                    amount=amount,
                    day=day
                )
                
                # Пересчёт суммы расходов за день
                updated_amount = sum(p.amount for p in Payment.objects.filter(day=day))
                print(updated_amount)
                day.amount += updated_amount
                print("======")
                print(day.amount)
                day.save()
                
                # Пересчёт общего баланса заказа
                order = day.order
                consumed_amount = sum(d.amount for d in Day.objects.filter(order=order))
                order.remains = order.amount - consumed_amount
                order.save()
                
                messages.success(request, f'Расходный материал "{new_consumable.name}" успешно добавлен.')
                return redirect('consumables', _id=_id)

        else:
            messages.warning(request, 'Необходимо заполнить все обязательные поля!')
    return render(request, 'program/add_payment.html', {
        'id': _id,
        'order_id': day.order.pk
    })