from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordChangeDoneView
from django.urls import include, path, reverse_lazy
from . import views

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.user_detail, name='user_detail'),
    path('profile/edit/', views.edit_user, name='edit_user'),
    path('profile/order/<int:pk>/', views.user_order, name='user_order'),
    path("password-reset/",
         views.CustomPasswordResetView.as_view(),
         name="password_reset"),
    path('password-reset/done/',
         PasswordResetDoneView.as_view(template_name="user/password_reset_done.html"),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
            template_name="user/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete")
         ),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         PasswordResetCompleteView.as_view(template_name="user/password_reset_complete.html"),
         name='password_reset_complete'),
    path('profile/password-change/', views.UserPasswordChange.as_view(), name="password_change"),
    path('profile/password-change/done/', PasswordChangeDoneView.as_view(template_name="user/password_change_done.html"), name="password_change_done"),
    
]
