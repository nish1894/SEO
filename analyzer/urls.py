from django.urls import path, include
from .views import *
urlpatterns = [
    path('', home_view, name ="analyzer"),
    path('analyze/', analyze_view, name='analyze'),
    path('history/<int:idx>/', history_detail, name='history_detail'),

]