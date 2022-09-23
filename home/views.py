from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import Users_Reg
from django.contrib.auth import authenticate, login
# Create your views here.
def home(request):
    return render(request, 'home/index.html')


def login_up(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('agregator')
        else:
            messages.success(request, f'Неправильно введен логин или пароль!')
    return render(request, 'home/index.html')


def create_user(request):
    if request.method == 'POST':
        new_user = Users_Reg()
        new_user.fio=request.POST['fio']
        new_user.bank=request.POST['bank']
        new_user.email = request.POST['email']
        new_user.comment=request.POST['comment']
        new_user.save()
        messages.success(request, f'Спасибо!\n'
                                  f'Ваша заявка принята!\n'
                                  f'Ожидайте транспортный пароль!\n')
        return redirect('home')
def update_email(request):
    if request.method == 'POST':
        newusername = request.POST['username']
        password = request.POST['password']
        password1 = request.POST['password1']
        if newusername!=request.user.username and password=='':
            user = User.objects.get(username=request.user.username)
            user.username = newusername
            user.save()
            messages.success(request, f'Ваша электронная почта изменена!')
        elif password!='':
            if password!=password1:
                messages.success(request, f'Пароли не совпадают.\n Изменения не могут быть сохранены!')
            else:
                try:
                    validate_password(password)
                    user = User.objects.get(username=request.user.username)
                    user.set_password(password)
                    if newusername==request.user.username:
                        user.save()
                        messages.success(request, f'Ваш пароль изменен!')
                    else:
                        user.username = newusername
                        user.save()
                        messages.success(request, f'Ваш пароль и электронная почта изменены!')
                except Exception as e:
                    messages.error(request, ''.join(e))
    return redirect('agregator')