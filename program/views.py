from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from decimal import Decimal
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from program.models import Orders, Day, Сonsumables, Payment

# --------------------------
# Аутентификация
# --------------------------

class CustomLoginView(LoginView):
    template_name = 'program/login.html'

def logout_view(request):
    logout(request)  # очищаем сессию
    return redirect('login')  # редирект на страницу логина

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Пользователь {user.username} успешно зарегистрирован!")
            return redirect('index')
        else:
            messages.error(request, "Ошибка регистрации. Проверьте введённые данные.")
    else:
        form = UserCreationForm()
    return render(request, 'program/register.html', {'form': form})

# --------------------------
# Главная страница
# --------------------------

@login_required
def index(request):
    orders = Orders.objects.all().order_by('-deadline')
    amount_total = sum(order.amount for order in orders)
    remains_total = sum(order.remains for order in orders)

    context = {
        'orders': orders,
        'amount': f"{amount_total:,}",
        'remains': f"{remains_total:,}"
    }
    return render(request, 'program/index.html', context)

# --------------------------
# Заказы
# --------------------------

@login_required
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

# --------------------------
# Дни заказов
# --------------------------

@login_required
def day(request, _id):
    days = Day.objects.filter(order__pk=_id).order_by('-date').select_related('order')
    for d in days:
        d.total_consumables_amount = sum(c.amount for c in Сonsumables.objects.filter(day=d)) + sum(p.amount for p in Payment.objects.filter(day=d))
    amount_total = sum(d.amount for d in days)
    return render(request, 'program/day.html', {
        'days': days,
        'amount': amount_total,
        'id': _id
    })

@login_required
def add_day(request, _id):
    order = get_object_or_404(Orders, pk=_id)
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

# --------------------------
# Расходные материалы
# --------------------------

@login_required
def consumables(request, _id):
    day = get_object_or_404(Day, pk=_id)
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

@login_required
def add_consumables(request, _id):
    day = get_object_or_404(Day, pk=_id)
    if request.method == 'POST':
        title = request.POST.get("title", "")
        count_str = request.POST.get("count", "").strip()
        prise_str = request.POST.get("prise", "").strip()
        unit = request.POST.get("unit", "")
        if title and count_str and prise_str and unit:
            try:
                count = Decimal(count_str)
                prise = Decimal(prise_str)
                new_c = Сonsumables.objects.create(
                    title=title,
                    count=count,
                    prise=prise,
                    amount=prise * count,
                    unit=unit,
                    day=day
                )
                _recalculate_day_and_order(day)
                messages.success(request, f'Расходный материал "{new_c.title}" успешно добавлен.')
                return redirect('consumables', _id=_id)
            except Exception as e:
                messages.error(request, f'Ошибка: {e}')
        else:
            messages.warning(request, 'Необходимо заполнить все поля!')
    return render(request, 'program/add_consumables.html', {'id': _id, 'order_id': day.order.pk})

@login_required
def add_payment(request, _id):
    day = get_object_or_404(Day, pk=_id)
    if request.method == 'POST':
        name = request.POST.get("name")
        amount_str = request.POST.get("amount")
        if name and amount_str:
            try:
                amount = Decimal(amount_str)
                new_p = Payment.objects.create(name=name, amount=amount, day=day)
                _recalculate_day_and_order(day)
                messages.success(request, f'Платёж "{new_p.name}" успешно добавлен.')
                return redirect('consumables', _id=_id)
            except Exception as e:
                messages.error(request, f'Ошибка: {e}')
        else:
            messages.warning(request, 'Необходимо заполнить все обязательные поля!')
    return render(request, 'program/add_payment.html', {'id': _id, 'order_id': day.order.pk})

# --------------------------
# Редактирование
# --------------------------

@login_required
def edit_consumables(request, _id):
    c = get_object_or_404(Сonsumables, pk=_id)
    day = c.day
    if request.method == 'POST':
        title = request.POST.get("title")
        count_str = request.POST.get("count")
        prise_str = request.POST.get("prise")
        unit = request.POST.get("unit")
        if title and count_str and prise_str and unit:
            try:
                c.title = title
                c.count = Decimal(count_str)
                c.prise = Decimal(prise_str)
                c.unit = unit
                c.amount = c.count * c.prise
                c.save()
                _recalculate_day_and_order(day)
                messages.success(request, "Материал успешно обновлён.")
                return redirect('consumables', _id=day.pk)
            except Exception as e:
                messages.error(request, f'Ошибка: {e}')
    return render(request, 'program/edit_consumables.html', {'consumable': c, 'id': day.pk, 'order_id': day.order.pk})

@login_required
def edit_payment(request, _id):
    p = get_object_or_404(Payment, pk=_id)
    day = p.day
    if request.method == 'POST':
        name = request.POST.get("name")
        amount_str = request.POST.get("amount")
        if name and amount_str:
            try:
                p.name = name
                p.amount = Decimal(amount_str)
                p.save()
                _recalculate_day_and_order(day)
                messages.success(request, "Платёж успешно обновлён.")
                return redirect('consumables', _id=day.pk)
            except Exception as e:
                messages.error(request, f'Ошибка: {e}')
    return render(request, 'program/edit_payment.html', {'payment': p, 'id': day.pk, 'order_id': day.order.pk})

# --------------------------
# Документы
# --------------------------

@login_required
def document(request, _id):
    day = get_object_or_404(Day, pk=_id)
    consum = Сonsumables.objects.filter(day=_id)
    paym = Payment.objects.filter(day=_id)
    return render(request, 'program/document.html', {
        'paym': paym,
        'consum': consum,
        'amount_consum': sum(c.amount for c in consum),
        'amount_paym': sum(p.amount for p in paym),
        'id': _id,
        'order_id': day.order.pk
    })

# --------------------------
# Вспомогательная функция
# --------------------------

def _recalculate_day_and_order(day):
    """Пересчёт суммы дня и остатка заказа"""
    total_consumables = sum(c.amount for c in Сonsumables.objects.filter(day=day))
    total_payments = sum(p.amount for p in Payment.objects.filter(day=day))
    day.amount = total_consumables + total_payments
    day.save()

    order = day.order
    consumed_amount = sum(d.amount for d in Day.objects.filter(order=order))
    order.remains = order.amount - consumed_amount
    order.save()