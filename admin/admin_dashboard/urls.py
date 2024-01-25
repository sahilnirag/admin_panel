from django.urls import path

from .views import *

app_name = "admin_dashboard"

urlpatterns = [
    path('', LogIn, name="login"),
    path('logout/', logout_user, name="logout_user"),
    path('dashboard/', dashboard, name="dashboard"),
    path('users/', users_listing, name="all_users"),
    path('users/<int:id>/<str:mode>/', add_update_user, name="user_view_edit"),
    path('users/delete/<int:id>/', delete_user, name="delete_user")
]