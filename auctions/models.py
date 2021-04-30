from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class listing(models.Model):
    user_name = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_info_listing")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    imageurl = models.CharField(max_length=64)
    category = models.CharField(max_length=64,default='Other')
    price = models.IntegerField(default='0')
    status = models.BooleanField(default=True)
    item_num = models.AutoField(primary_key=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="winner_user_info_listing",null=True,blank=True)

    def __str__(self):
        return f"Item Number: {self.item_num} {self.title} and {self.description} and {self.imageurl}"

class Bids(models.Model):
    starting_bid = models.IntegerField(default='0')
    current_bid = models.IntegerField(default='0')
    previous_bid = models.IntegerField(default='0')
    listing_info = models.ForeignKey(listing,on_delete=models.CASCADE,related_name="listing_info_bids")
    user_name = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_info_bids")

    def __str__(self):
        return f"{self.listing_info}"

class Comments(models.Model):
    user_name = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_info_comments")
    listing_info = models.ForeignKey(listing,on_delete=models.CASCADE,related_name="listing_info_comments")
    comment = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.listing_info}"

class watchlist(models.Model):
    user_name = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_info_watchlist")
    listings = models.ForeignKey(listing,on_delete=models.CASCADE,related_name="listing_info_watchlist")

    def __str__(self):
        return f"{self.user_name} and {self.listings}"