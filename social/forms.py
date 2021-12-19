from django import forms
from phonenumber_field.formfields import PhoneNumberField
from .models import SpecificUser, Comment, Post


class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = SpecificUser
        fields = ['username', 'password']

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = SpecificUser.objects.filter(username=username).first()
        if not user:
            raise forms.ValidationError(f'Пользователь с логином {username} не найден в системе')
        if not user.check_password(password):
            raise forms.ValidationError(f'Неверный пароль')
        return self.cleaned_data


class SettingsForm(forms.ModelForm):

    birthday = forms.DateField(
        widget=forms.DateInput(format=('%d-%m-%Y'), attrs={'class': 'form-control', 'type': 'date'}), required=False)
    phone = PhoneNumberField(required=False)

    class Meta:
        model = SpecificUser
        fields = ['first_name', 'last_name', 'email', 'bio', 'birthday', 'gender', 'phone', 'avatar']


class RegistrationForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    birthday = forms.DateField(widget=forms.DateInput(format=('%d-%m-%Y'), attrs={'class':'form-control', 'type':'date'}))
    email = forms.EmailField()

    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError('Пароли не совпадают')
        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if SpecificUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Данный почтовый ящик уже зарегистрирован')
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if SpecificUser.objects.filter(phone=phone).exists():
            raise forms.ValidationError('Данный телефон уже зарегистрирован')
        return phone

    class Meta:
        model = SpecificUser
        fields = ['username', 'password', 'confirm_password', 'first_name', 'last_name',
                  'email', 'bio', 'birthday', 'gender', 'phone', 'avatar']


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text')
