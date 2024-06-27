from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.store, name='storepage'),
    path('checkout/', views.checkout, name='checkoutpage'),
    path('cart/', views.cart, name='cartpage'),
    path('updateitem/', views.update_item, name='updateitempage'),
    path('processorder/', views.process_order, name='processorderpage'),
    path('login/', views.login_view, name='loginpage'),
    path('logout/', views.logout_view, name='logoutpage'),
    path('register/', views.register_view, name='resgisterpage'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profile/', views.update_profile, name='profilepage'),
    path('profile/password_change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change_form.html',
    ), name='password_change'),
    path('profile/password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),
    path('about/',views.about_page, name='aboutpage'),
    path('contact_us/',views.contact_page, name='contactuspage'),
    path('feedback/',views.feedback_page, name='feedbackpage'),
]

