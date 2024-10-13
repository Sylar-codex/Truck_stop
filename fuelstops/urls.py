from django.urls import path, include
from .api import DestinationAPI

urlpatterns = [
    path("api/your_start_&_finish/", DestinationAPI.as_view())
]