"""complimentapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_framework_nested import routers

from complimentapi.views import AuthViewSet, ReceiverViewSet, ComplimentViewSet


router = routers.SimpleRouter(trailing_slash=False)

router.register(r'auth', AuthViewSet, basename='auth')

router.register(r'receivers', ReceiverViewSet, basename='receivers')

receiver_router = routers.NestedSimpleRouter(router, r'receivers', lookup='receiver')
receiver_router.register(r'compliments', ComplimentViewSet, basename='compliments')

urlpatterns = router.urls
urlpatterns += receiver_router.urls
