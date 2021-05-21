from django.shortcuts import render
# django 
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, Http404
from django.utils.translation import ugettext as _
from django.conf import settings

# user login/logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# forms 
from apnea_detection.forms import LoginForm, RegisterForm, SetupForm

# file i/o
import pandas as pd
import os

ROOT_DIR = os.getcwd() 
DATA_DIR = os.path.join(ROOT_DIR, "data")


@login_required
def home(request):
    context = {}
    
    return render(request, "apnea_detection/home.html", context=context)

@login_required
def setup(request):
    print(os.getcwd())
    if request.method == "POST":
        form = SetupForm(request.POST)
        if form.is_valid():
            normalize(form.cleaned_data)
            form.save()
    form = SetupForm()
    context = {'form': form}
    return render(request, "apnea_detection/setup.html", context=context)

''' Normalizes a file specified by user '''
def normalize(form):
    excerpt             = form["excerpt"]
    dataset             = form["dataset"]
    apnea_type          = form["apnea_type"]
    norm                = form["norm"]
    slope_threshold     = form["slope_threshold"]
    scale_factor_low    = form["scale_factor_low"]
    scale_factor_high   = form["scale_factor_high"]

    file_in = f"{DATA_DIR}/{dataset}/preprocessing/excerpt{excerpt}/filtered_8hz.txt"
    df = pd.read_csv(file_in, delimiter=",")
    # perform linear scaling
    df["Value"] = df["Value"] * scale_factor_high
    file_out = file_in.split('.')[0] + f"_{norm}_{scale_factor_high}" + ".norm"
    df.to_csv(file_out, index=None, float_format='%.6f')

@login_required
def prediction(request):
    context = {}
    # latest 
    return render(request, "apnea_detection/prediction.html", context=context)


@login_required
def results(request):
    context = {}
    cols = ["data","apnea_type","num_pos_train","num_neg_train",\
            "f1_1","f1_0","true_pos","true_neg","false_pos","false_neg"]

    results_df = pd.read_csv("apnea_detection/results.csv", names=cols)
    context["results_html"] = results_df.to_html()
    return render(request, "apnea_detection/results.html", context=context)

#####################################################################
#                     User Registration
####################################################################
def register_action(request):
    context = {}

    # If GET request, display blank registration form
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'apnea_detection/register.html', context)

    # If POST request, validate the form
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'apnea_detection/register.html', context)


    # Register and login new user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    # Saves new user profile, authenticate 
    new_user.save()
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    # Login
    login(request, new_user)
    return redirect(reverse('home'))

#####################################################################
#                     Logout action
####################################################################
def logout_action(request):
    logout(request)
    return redirect(reverse('login'))


#####################################################################
#                           Login
####################################################################
def login_action(request):

    context = {}

    # If GET request
    if request.method == 'GET':
        # If user already logged in, go to global stream page 
        if request.user.is_authenticated:
            return redirect(reverse('home'))  
        else:
            context['form'] = LoginForm()
            context["title"] = "Login"
            return render(request, 'apnea_detection/login.html', context)
        

    # If POST request, validate login form 
    form = LoginForm(request.POST)
    context['form'] = form

    # If not valid form 
    if not form.is_valid():
        print('Invalid login')
        return render(request, 'apnea_detection/login.html', context)

    # Authenticate user and log in
    username = form.cleaned_data['username']
    password = form.cleaned_data['password']
    user = authenticate(username=username, password=password)
    login(request, user)
    return redirect('/')