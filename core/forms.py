from django import forms
from django.contrib.auth import authenticate


class LoginForm(forms.Form):
    """Custom login form.
    
    For development, we use Django's authentication system.
    """
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput())
    
    def clean(self):
        """Validate login info."""
        data = self.cleaned_data
        username = data.get('username')
        password = data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                self.user = user
            else:
                self.add_error('username', 'The provided login details are invalid.')
        return data