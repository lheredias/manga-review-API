# todo/todo/urls.py : Main urls.py
from django.contrib import admin
from django.urls import path, re_path, include
from knox import views as knox_views
from .views import (SeriesListApiView, ReviewListApiView, 
SeriesDetailApiView, ReviewDetailApiView, RegisterApiView, 
LoginAPI, UserListApiView, UserDetailApiView, 
ReviewLikeListApiView, ReviewUnlikeListApiView, LikedReviewListApiView)


urlpatterns = [
    path('series/', SeriesListApiView.as_view()),
    path('users/', UserListApiView.as_view()),
    path('users/<int:user_id>/', UserDetailApiView.as_view()),
    path('register/', RegisterApiView.as_view()),
    path('login/', LoginAPI.as_view()),
    path('logout/', knox_views.LogoutView.as_view()),
    path('series/<int:series_pk>/', SeriesDetailApiView.as_view()),
    path('series/<int:series_pk>/reviews/', ReviewListApiView.as_view()),
    path('series/<int:series_pk>/reviews/<int:review_pk>/', ReviewDetailApiView.as_view()),
    path('series/<int:series_pk>/reviews/<int:review_pk>/like/', ReviewLikeListApiView.as_view()),
    path('series/<int:series_pk>/reviews/<int:review_pk>/unlike/', ReviewUnlikeListApiView.as_view()),
    path('liked_reviews/', LikedReviewListApiView.as_view()),

]

