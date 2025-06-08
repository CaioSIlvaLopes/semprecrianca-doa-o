from django.contrib import admin
from django.urls import path
from donate.views import principal_view, donate_view,pagamentos_view
from django.urls import path
from donate import views
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', principal_view, name='home'),           # Página principal
    path('donate/', donate_view, name='donate'),     # <-- nome da URL aqui!
    path("webhook/stripe/", views.stripe_webhook, name="stripe-webhook"),
    path('pagamentos/', pagamentos_view, name='pagamentos'),
     path('criar-pagamento/', views.criar_pagamento, name='criar_pagamento'),
]