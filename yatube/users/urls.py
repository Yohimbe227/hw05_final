from django.contrib.auth import views as vw
from django.urls import path, include

from users import views
from users.apps import UsersConfig

app_name = UsersConfig.name

passwords = [
    path(
        'password_change/done/',
        vw.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html',
        ),
        name='password_change_done',
    ),
    path(
        'password_change/',
        vw.PasswordChangeView.as_view(
            template_name='users/password_change_form.html',
        ),
        name='password_change_form',
    ),
    path(
        'password_reset/done/',
        vw.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'password_reset/',
        vw.PasswordResetView.as_view(
            template_name='users/password_reset_form.html',
        ),
        name='password_reset_form',
    ),
    path(
        'reset/<uidb64>/<token>/',
        vw.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        vw.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
]

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        vw.LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout',
    ),
    path(
        'login/',
        vw.LoginView.as_view(template_name='users/login.html'),
        name='login',
    ),
    path('passwords/', include(passwords)),
]
