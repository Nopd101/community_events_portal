from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    #path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path("route-after-login/", views.route_after_login, name="route_after_login"),
    path('logout/', views.logout_user, name="logout"),
    path("admin/users/<int:pk>/edit/", views.admin_user_edit, name="admin_user_edit"),
    path("admin/users/<int:pk>/delete/", views.admin_user_delete, name="admin_user_delete"),
]