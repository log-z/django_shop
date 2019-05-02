from django import forms


class RegisterBbForm(forms.Form):
    """后端用户注册表单：主要用于验证"""

    username = forms.CharField(label='用户名', min_length=3, max_length=20)
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='密码', min_length=64, max_length=64)


class RegisterFbForm(RegisterBbForm):
    """前端用户注册表单：主要用于显示"""

    password = forms.CharField(label='密码', min_length=8, max_length=20, widget=forms.PasswordInput())
    password_again = forms.CharField(label='重复密码', min_length=8, max_length=20, widget=forms.PasswordInput())
