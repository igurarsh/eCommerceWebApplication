from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create",views.create,name="create"),
    path("listing/<str:title>/<int:num>",views.listingpage,name="listingpage"),
    path("save/<str:title>/<str:tit>/<int:num>",views.add_watchlist,name="watchlistpage"),
    path("placebid/<str:title>/<int:num>",views.place_bids,name="placebid"),
    path("close/<str:title>/<int:num>",views.close_list,name="close_auct"),
    path("addcmt/<str:title>/<int:num>",views.place_comments,name="placecmt"),
    path("watchlist",views.watch_list,name="watchlist"),
    path("ucategory",views.show_category,name="ucategory"),
    path("result",views.show_results,name="results")
]
