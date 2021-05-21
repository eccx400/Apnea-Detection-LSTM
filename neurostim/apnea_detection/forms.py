from django import forms 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from apnea_detection.models import Setup, ModelParams

# max image size 
MAX_UPLOAD_SIZE = 2500000

# login form 
class LoginForm(forms.Form):
    username    = forms.CharField(max_length = 20)
    password    = forms.CharField(max_length = 200, widget = forms.PasswordInput())
    
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                "name":field})

    def clean(self, *args, **kwargs):
        # Confirms that the two password fields match
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
         
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Invalid username/password")
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect Password")
            # We must return the cleaned data we got from our parent.
        return super(LoginForm, self).clean(*args, **kwargs)


# registration form 
class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name  = forms.CharField(max_length=20)
    email      = forms.CharField(max_length=50,
                                 widget = forms.EmailInput())
    username   = forms.CharField(max_length = 20)
    password  = forms.CharField(max_length = 200, 
                                 label='Password', 
                                 widget = forms.PasswordInput())
    confirm_password = forms.CharField(max_length = 200, 
                                 label='Confirm password',  
                                 widget = forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                "name":field})
        

    def clean(self):
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username


# Normalization
class SetupForm(forms.ModelForm):
  
    class Meta:
        model = Setup
        exclude = []

# ML Model
# Normalization
class ModelParamsForm(forms.ModelForm):
  
    class Meta:
        model = ModelParams
        exclude = []