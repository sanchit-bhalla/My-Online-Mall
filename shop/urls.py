from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name='ShopHome'),
    path("about/", views.about, name='AboutUs'),
    path("contact", views.contact, name='ContactUs'),
    path("tracker/", views.tracker, name='TrackingStatus'),
    path("search/", views.search, name='Search'),
    path("products/<int:myid>", views.prViews, name='ProductView'),
    path("checkout/", views.CheckOutView.as_view(), name='Checkout'),

    #                For stripe payment integration
    path('charge/', views.charge, name='charge'),
]
