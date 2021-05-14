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
    path('setup/', views.setup, name="setup"),
    path('normalization/', views.normalization, name="normalization"),
    path('prediction/', views.prediction, name="prediction"),
    path('results/', views.results, name="results")
]