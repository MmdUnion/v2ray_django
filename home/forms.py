from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, label="", required=True, widget=forms.TextInput(attrs={"class":"form-control mb-2", "aria-describedby":"usernameHelp", "placeholder":"نام کاربری"}))


    password = forms.CharField(max_length=50, label="", required=True, widget=forms.PasswordInput(attrs={"class":"form-control", "placeholder":"رمز عبور"}))


    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if len(username) > 50:
            self.add_error("username", "نام کاربری حداکثر میتواند 50 حرف باشد")

        if len(password) > 50:
            self.add_error("password", "رمز عبور حداکثر میتواند 50 حرف باشد")



