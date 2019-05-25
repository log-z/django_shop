from django import forms


class LoginBEForm(forms.Form):
    """后端用户登陆表单：主要用于验证"""

    username = forms.CharField(label='用户名', min_length=3, max_length=20)
    password = forms.CharField(label='密码', min_length=64, max_length=64)


class LoginFEForm(LoginBEForm):
    """前端用户登陆表单：主要用于显示"""

    password = forms.CharField(label='密码', min_length=8, max_length=20, widget=forms.PasswordInput())
    field_order = ['username', 'email', 'password']


class RegisterBEForm(LoginBEForm):
    """后端用户注册表单：主要用于验证"""

    email = forms.EmailField(label='Email')


class RegisterFEForm(LoginFEForm, RegisterBEForm):
    """前端用户注册表单：主要用于显示"""

    password_again = forms.CharField(label='重复密码', min_length=8, max_length=20, widget=forms.PasswordInput())
    field_order = ['username', 'email', 'password', 'password_again']
