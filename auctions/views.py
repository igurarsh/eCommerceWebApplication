from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from django.urls import reverse

from django import forms
from django.core.files import File
from .models import *
import numpy as np
import urllib
import cv2

# Category options for user
Category_choices = [
    ('electronic','Electronics'),
    ('clothing','Clothing'),
    ('eat','Eating'),
    ('entertainment','Entertainment'),
    ('realestate','Real-Estate'),
    ('others','Other'),
]

# Stuff to download image and show it in index page
def index(request):
    # Getting all the listing availables from the database
    return render(request, "auctions/index.html",{
        "data_listing":listing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

# Function where user can make new listing

class get_info(forms.Form):
    Title = forms.CharField(widget=forms.TextInput(attrs={'class' : 'create_tit'}),label='')
    Description = forms.CharField(widget=forms.TextInput(attrs={'class' : 'create_tit'}),label='')
    Image_url = forms.CharField(widget=forms.TextInput(attrs={'class' : 'create_tit'}),label='')
    Price = forms.IntegerField(widget=forms.NumberInput(attrs={'class' : 'create_tit'}),label='')
    Category = forms.CharField(widget=forms.Select(choices=Category_choices,attrs={'class' : 'create_tit'}),label='')

def create(request):

    # Access the user name of user
    current_username = request.user.username
    username = User.objects.get(username=current_username)
    
    # checking if the request method is post
    if request.method == "POST":
        # Getting user information to store in the table 
        form = get_info(request.POST)

        # checking if the form is valid 
        if form.is_valid():
            title = form.cleaned_data["Title"]
            description = form.cleaned_data["Description"]
            i_url = form.cleaned_data["Image_url"]
            category = form.cleaned_data["Category"]
            price = form.cleaned_data["Price"]

            # saving all data in data base
            temp_data = listing(title=title,description=description,imageurl=i_url,user_name=username,category=category,price=price)
            temp_data.save()

        else:
            return render(request,"auctions/create.html",{
                "info_form":get_info()
            })

    return render(request,"auctions/create.html",{
        "info_form":get_info()
    })

# Function for listing page
def listingpage(request,title,num):
    # checking if the title exits in the database or not
    database = listing.objects.all()

    # creating title for watch list depending upon database
    watch_title = "Add To Watchlist"
    try:
        title_vali=watchlist.objects.get(listings=listing.objects.get(item_num=num,title=title),user_name=User.objects.get(username=request.user.username))
    except:
        title_vali=None
    
    if(title_vali!=None):
        watch_title="Remove from Watchlist"
    
    # code for bid 
    cur_bid = 0

    try:
        bid_data = Bids.objects.get(listing_info=listing.objects.get(item_num=num,title=title))
        cur_bid = bid_data.current_bid
    except:
        pass
    
    # Code for checking if the user who created the list is logged in and if auction is closed
    owner = False
    auction_status = True
    winner_name =""
    try:
        temp_user = User.objects.get(username=request.user.username)
        temp_user_listing = listing.objects.get(item_num=num,title=title)
        # Getting winner info
        if(temp_user_listing.status == False):
            winner_name = temp_user_listing.winner
            auction_status = False

        # checking if owner is logged in    
        if(temp_user == temp_user_listing.user_name):
            owner = True
    except:
        owner = False    
        auction_status = True

    # Getting comments from database
    cmt_data = Comments.objects.filter(listing_info=listing.objects.get(title=title,item_num=num))

    # code for passing data in webpage
    for data in database:
        if data.title == title:
            return render(request,"auctions/listingpage.html",{
                "info":database.get(title=data.title,item_num=num),
                "watch_title":watch_title,
                "current_bid":cur_bid,
                "owner_vali":owner,
                "post_vali":auction_status,
                "winner_info":winner_name,
                "comment_data":cmt_data
            })

    # if all Validations got failed
    return HttpResponse("Ttitle not found")
    #return render(request,"auctions/listingpage.html")

#---------------------------------------------------------#

def add_watchlist(request,title,tit,num):
    # Getting all database to check title validation

    # Checking if user is logged in or not 
    try:
        current_username = request.user.username
        username = User.objects.get(username=current_username)
    except:
        return redirect('login')

    database = listing.objects.all()

    if(tit=="Remove from Watchlist"):
        try:
            watchlist.objects.get(user_name=username,listings=listing.objects.get(title=title,item_num=num)).delete()
            return redirect('listingpage',title,num)
        except:
            return redirect('listingpage',title,num)

    # Checking if title already exists
    try:
        if(watchlist.objects.get(user_name=username,listings=listing.objects.get(title=title,item_num=num))):
            return redirect('listingpage',title)
    except:
        # if all validations got passed save data in database
        for data in database:
            if data.title == title:
                list_info = database.get(title=data.title,item_num=num)
                temp_store = watchlist(user_name=username,listings=list_info)
                temp_store.save()
                return redirect('listingpage',title,num)

    return HttpResponse("Ttitle not found")

#---------------------------------------------------------#

# Function for bids functionality on listing page
def place_bids(request,title,num):
    if request.method == "POST":

        # Getting current username
        current_username = request.user.username

        amt = int(request.POST['bidamt'])
        # if any bid already exits
        try:
            # getting the bid database
            list_data = listing.objects.get(title=title,item_num=num)
            bid_data = Bids.objects.get(listing_info=list_data)
            cur_old_price = bid_data.current_bid
            starting_old_price = bid_data.starting_bid
            previous_old_price = bid_data.previous_bid
            # now checking if user value get passes
            if (amt>cur_old_price and amt>starting_old_price and amt>previous_old_price):
                Bids.objects.get(listing_info=list_data).delete()
                temp_data = Bids(listing_info=list_data,user_name=User.objects.get(username=current_username),starting_bid=starting_old_price,current_bid=amt,previous_bid=previous_old_price)
                temp_data.save()
                return redirect("listingpage",title,num)
            return redirect("listingpage",title,num)
        # if bid does not exists
        except:
            list_data = listing.objects.get(title=title,item_num=num)
            amount = amt
            if(amount>list_data.price):
                temp_data = Bids(listing_info=list_data,user_name=User.objects.get(username=current_username),starting_bid=amt,current_bid=amt,previous_bid=list_data.price)
                temp_data.save()
                return redirect("listingpage",title,num)
            return redirect("listingpage",title,num)

#---------------------------------------------------------#

def close_list(request,title,num):
    # checking if the user who is logged in requested to close auction
    owner = False
    # Getting user info, bids and listing info from database
    try:
        temp_user_listing = listing.objects.get(item_num=num,title=title)
        temp_user = User.objects.get(username=request.user.username)
        temp_bids = Bids.objects.get(listing_info=temp_user_listing)
    except:
        return HttpResponse("Something went wrong please try again")

    # verifying the user requested to close the auction is same who made the auction
    try:
        if(temp_user == temp_user_listing.user_name):
            owner = True
    except:
        owner = False

    # if validation passes change the status of listing to false
    try:
        # closing the auct and making higher bid user winner
        if owner:
            temp_user_listing.status = False
            temp_user_listing.winner = temp_bids.user_name
            temp_user_listing.save()
            return redirect(listingpage,title,num)
    except:
        redirect(listingpage,title,num)

#---------------------------------------------------------#

# function for placing comments
def place_comments(request,title,num):
    # Getting user data
    if request.method == "POST":
        usr_comment = request.POST["comments"]
        # Getting user info and listing database info
        try:
            temp_listing = listing.objects.get(title=title,item_num=num)
            usr_name = request.user.username
            temp_user = User.objects.get(username=usr_name)
            temp_cmt = Comments(user_name=temp_user,listing_info=temp_listing,comment=usr_comment)
            temp_cmt.save()
            # return to listing page
            return redirect('listingpage',title,num)
        except:
           return HttpResponse("Something went wrong") 
    # If something went wrong
    return HttpResponse("Something went wrong")

#---------------------------------------------------------#

# function for watchlist page
def watch_list(request):
    # checking if user is logged in
    if request.user.username:
        # Getting wacthlist datbase
        try:
            temp_watch = watchlist.objects.filter(user_name=User.objects.get(username=request.user.username))
        except:
            error_var = "Watchlist empty"
        
        return render(request,'auctions/watchlist.html',{
            "watch_data":temp_watch
        })

#---------------------------------------------------------#

# Function for category page
class get_category(forms.Form):
    Category = forms.CharField(widget=forms.Select(choices=Category_choices,attrs={'class' : 'create_tit'}),label='')

def show_category(request):

    return render(request,'auctions/category.html',{
        "info_cat":get_category()

    })

def show_results(request):

    if request.method == "POST":
        # getting user selection
        form = get_category(request.POST)

        # checking if the form is valid 
        if form.is_valid():
            usr_option = form.cleaned_data['Category']
            
            # getting result from database
            try:
                temp_data = listing.objects.filter(category=usr_option)
            except:
                return HttpResponse("something went wrong in try "+usr_option)

            # Passing data to website
            return render(request,'auctions/category.html',{
                    "info_cat":get_category(),
                    "search_result":temp_data
                })

    # If nothing works
    return HttpResponse("something went wrong")