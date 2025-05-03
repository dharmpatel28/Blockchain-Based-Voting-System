from django import forms

class AdminLoginForm(forms.Form):
    private_key = forms.CharField(widget=forms.PasswordInput)

class AddCandidateForm(forms.Form):
    name = forms.CharField()

class RegisterVoterForm(forms.Form):
    address = forms.CharField()
    name = forms.CharField()
