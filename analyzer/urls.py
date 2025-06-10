from django.urls import path, include
from .views import *
urlpatterns = [
    path('', home_view, name ="analyzer"),
    path('analyze/', analyze_view, name='analyze'),

]