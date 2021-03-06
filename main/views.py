# 직접 개발한 코드
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from main.forms import UserCreationForm
from main.models import User, ApiKey, Domain

from urllib.parse import urlparse
import json
import jwt


def index(request):
    context = {

    }
    return render(request, 'main/pages/index.html', context)


def user_signup(request):
    context = {

    }
    if request.is_ajax():
        response_data = {}

        data = json.loads(request.body.decode('utf-8'))
        postEmail = data.get('email')
        postUsername = data.get('username')
        postPassword = data.get('password')

        user = User(email=postEmail, username=postUsername)
        user.set_password(postPassword)
        try:
            user.save()

        except IntegrityError as e:
            response_data['status'] = False
            response_data['msg'] = 'Sorry! This email is already signed up.'
            return HttpResponse(json.dumps(response_data),
                                content_type="application/json"
                                )
        response_data['status'] = True
        response_data['msg'] = 'Success!'

        return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )


    else:
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()

        else:
            form = UserCreationForm()

        context.update({'form': form})
        return render(request, 'main/pages/signup.html', context)


def user_login(request):

    context = {}

    if request.is_ajax():
        response_data = {}
        data = json.loads(request.body.decode('utf-8'))
        postEmail = data.get('email')
        postPassword = data.get('password')

        try:
            user = authenticate(email=postEmail, password=postPassword)
        except:
            return JsonResponse({'error': 'no user'})

        if user is not None:
                if user.is_active:
                    login(request, user)
                    return JsonResponse({'status': 'success'})

        return JsonResponse({})


def user_logout(request):
    logout(request)
    return redirect('main:index')


@login_required
def user_mypage(request, id):
    context = {
        'userId': id
    }

    u = User.objects.get(id=id)
    try:
        a = ApiKey.objects.get(user=u)
        d = Domain.objects.filter(api_key=a)
    except ObjectDoesNotExist:
        pass

    context.update({
        'api_key': a,
        'domains': d
    })
    return render(request, 'main/pages/mypage.html', context)


@login_required
def apikey_new(request):
    context = {}
    if request.method == 'POST':
        ApiKey.objects.generate(request.user)
        return redirect('main:user_mypage', request.user.id)
    else:
        return render(request, 'main/pages/apikey_new.html', context)


@login_required
def domain_new(request):
    context = {}
    if request.method == 'POST':
        domain = request.POST.get('domain')
        parsed_domain = urlparse(domain)

        if parsed_domain.path[:9] == '127.0.0.1' or parsed_domain.path[:9] == 'localhost':
            post_domain = parsed_domain.path

        elif parsed_domain.netloc:
            post_domain = parsed_domain.netloc
            if post_domain[:4] == 'www.':
                post_domain = post_domain[4:]
        else:
            post_domain = parsed_domain.path

        if not post_domain:
            messages.add_message(request, messages.ERROR, 'Please write a right url.')
            return redirect('main:user_mypage', request.user.id)

        try:
            a = ApiKey.objects.get(key=request.POST.get('api_key'))
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, 'api key doesn\'t exist.')
            return redirect('main:user_mypage', request.user.id)

        d = Domain(domain=post_domain, api_key=a)
        d.save()
    return redirect('main:user_mypage', request.user.id)


def secret_key_new(request, key):
    a = get_object_or_404(ApiKey, key=key)
    a.secret_key = ApiKey.objects.generate_secret()
    a.save()
    return redirect('main:user_mypage', request.user.id)


@csrf_exempt
def jwt_new(request):
    data = json.loads(request.body.decode('utf-8'))
    api_key = data.get('api-key')
    secret = data.get('secret-key')
    exp = data.get('exp')
    nbf = data.get('nbf')
    if not exp:
        exp = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    if not nbf:
        nbf = datetime.datetime.utcnow()

    a = get_object_or_404(ApiKey, key=api_key)
    if a.secret_key == secret:
        encoded = jwt.encode({
            'api-key': api_key,
            'exp': exp,
            'nbf': nbf
        }, secret, algorithm='HS256')

        return JsonResponse({'jwt': str(encoded.decode('utf-8'))})
    else:
        return JsonResponse({'error': 'Not valid secret key.'})

def dashboard_overview(request):
    return render(request, 'vote/pages/multi_dashboard.html')

def dashboard_filter(request):
    return render(request, 'vote/pages/multi_dashboard_2.html')

def dashboard_users(request):
    return render(request, 'vote/pages/multi_dashboard_3.html')