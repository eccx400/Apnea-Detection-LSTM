from django.urls import path
from apnea_detection import views 

urlpatterns =[ 
    # login/logout 
    path('login/', views.login_action, name="login"),
    path('register/', views.register_action, name="register"),
    path('logout/', views.logout_action, name="logout"),
    # home
    path('home', views.home, name="home"),

    # pipeline
    path('setup/', views.logout_action, name="setup"),
    path('normalization/', views.logout_action, name="normalization"),
    path('prediction/', views.logout_action, name="prediction")
]