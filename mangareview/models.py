from pyexpat import model
from tkinter import CASCADE
from unicodedata import name
from wsgiref.validate import validator
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator 
from datetime import date
from django.core.exceptions import ValidationError

def genre_validator(genres_input):
    GENRES = ["shonen", "shojo", "seinen", "romance",
    "sports", "action", "adventure", "comedy", "drama",
    "slice of life", "fantasy", "horror", "psychological",
    "mecha", "historical", "cyberpunk"]
    for genre in genres_input:
      if genre not in GENRES:
        raise ValidationError(
          f"/{genre}/ is not a valid genre")
  
class Series(models.Model):
  
  title = models.CharField(max_length = 180)
  author=models.CharField(max_length = 180)
  rating = models.FloatField(blank=True,null=True)
  genre=models.JSONField(validators=[genre_validator])
  year = models.PositiveIntegerField(validators=
  [MinValueValidator(1900), 
  MaxValueValidator(date.today().year)])
  about = models.CharField(max_length = 3000,default="")
  completed = models.BooleanField(default=False)
  anime = models.BooleanField(default=False)
  chapters = models.PositiveIntegerField(blank=True,null=True)
  volumes = models.PositiveIntegerField(blank=True,null=True)
  official_translation=models.BooleanField(default=False)

  @property
  def get_rating(self):
    ratings=[]
    likes=[]
    for review in self.reviews.all():
      ratings.append(review.rating)
      likes.append(review.likes.count()+1)  
    return round(sum([(a*b)/sum(likes) for a,b in zip(ratings,likes)]),2)
    
  def update(self, *args, **kwargs):
      if self.reviews.exists():
        self.rating = self.get_rating
      else:
        self.rating = None
      super(Series, self).save(*args, **kwargs)

  class Meta:
    ordering = ['-pk']

    constraints = [models.UniqueConstraint(
      fields=('title', 'author'), name='unique_series')]

  def __str__(self):
    return self.title

class Review(models.Model):
  reviewer=models.ForeignKey(User,on_delete=models.CASCADE,related_name="reviews")
  content = models.TextField(max_length = 5000)
  rating = models.FloatField(validators=
  [MinValueValidator(0), 
  MaxValueValidator(10)])
  likes=models.ManyToManyField(User,blank=True,related_name="liked")
  date=models.DateField(auto_now_add=True)
  series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name="reviews")

  def __str__(self):
    return f"Review from {self.reviewer.username} for {self.series.title}"
  class Meta:
    ordering = ['-pk']