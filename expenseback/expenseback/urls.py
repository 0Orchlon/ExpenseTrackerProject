from django.urls import path
from backend import views,edituser

urlpatterns = [
    path('user/', views.checkService), # localhost:8000/api/users/ gehed views.checkService function duudna.
    path('useredit/', edituser.editcheckService), # localhost:8000/api/useredit/ gehed edituser.editcheckService function duudna.
]
