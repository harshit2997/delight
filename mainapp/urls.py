"""delight URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.home,name="home"),
    url(r'^menu/$', views.menu,name="menu"),
    url(r'^edit_dish/$', views.edit_dish, name='edit_dish'),
    url(r'^delete_dish/$', views.delete_dish, name='delete_dish'),
    url(r'^add_dish/$', views.add_dish, name='add_dish'),
    url(r'^register/$', views.register,name="register"),
    url(r'^create_acc/$', views.create_acc,name="create_acc"),
    url(r'^logout/$', views.logout,name="logout"),
    url(r'^login/$', views.login,name="login"),
    url(r'^emp_det/$', views.emp_det,name="emp_det"),
    url(r'^edit_emp/$', views.edit_emp,name="edit_emp"),
    url(r'^delete_emp/$', views.delete_emp,name="delete_emp"),
    url(r'^add_emp/$', views.add_emp,name="add_emp"),
    url(r'^add_mgr/$', views.add_mgr,name="add_mgr"),
    url(r'^profile/$', views.profile,name="profile"),
    url(r'^edit_profile_cust/$', views.edit_profile_cust,name="edit_profile_cust"),
    url(r'^edit_profile_emp/$', views.edit_profile_emp,name="edit_profile_emp"),
    url(r'^refreshmodal/$', views.refreshmodal,name="refreshmodal"),
    url(r'^offers/$', views.offers,name="offers"),
    url(r'^delete_offer/$', views.delete_offer,name="delete_offer"),
    url(r'^edit_offer/$', views.edit_offer,name="edit_offer"),
    url(r'^add_offer/$', views.add_offer,name="add_offer"),
    url(r'^add_to_order/$', views.add_to_order,name="add_to_order"),
    url(r'^checkout/$', views.checkout,name="checkout"),
    url(r'^increment/$', views.increment,name="increment"),
    url(r'^decrement/$', views.decrement,name="decrement"),
    url(r'^final/$', views.final,name="final"),
    url(r'^prev/$', views.prev,name="prev"),
    url(r'^process/$', views.process,name="process"),


]
