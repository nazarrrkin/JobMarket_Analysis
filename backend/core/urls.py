
from django.urls import path

from core.views import ParserDataView

urlpatterns = [
    path('take-data/', ParserDataView.as_view({'post':'post'}))
]
