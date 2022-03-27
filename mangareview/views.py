from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Series, Review, User
from .serializers import SeriesSerializer, ReviewSerializer, RegisterSerializer, UserSerializer
from rest_framework.renderers import JSONRenderer
from knox.models import AuthToken
from django.contrib.auth import login
from knox.views import LoginView as KnoxLoginView
from rest_framework.authtoken.serializers import AuthTokenSerializer
from .permissions import *
# from drf_yasg.utils import swagger_auto_schema

class RegisterApiView(APIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    # @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request, *args, **kwargs):
        '''
        User registration.
        '''
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": serializer.data,
                "token": AuthToken.objects.create(user)[1]},
                status=status.HTTP_201_CREATED
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPI(KnoxLoginView):
    
    serializer_class = AuthTokenSerializer

    permission_classes = [permissions.AllowAny]
    # @swagger_auto_schema(request_body=AuthTokenSerializer)

    def post(self, request, format=None):
        '''
        Retrieves a token that expires in 4 hours or when user logs out.
        This token shall be used (as a header parameter) in all requests that require authentication like so:
        Authetication: Token [TOKEN]
        '''
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)

class UserListApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    # 1. List all
    def get(self, request, *args, **kwargs):
        
        '''
        Retrieves users list. Requires authentication.
        '''
        user_list = User.objects.all()
        serializer = UserSerializer(user_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserDetailApiView(APIView):
    permission_classes = [permissions.IsAdminUser, permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, user_id):
        '''
        Helper method to get the object with given user_id
        '''
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    # 3. Retrieve
    def get(self, request, user_id, *args, **kwargs):
        '''
        Retrieves user details given an user_id. Requires authentication.
        '''
        user_instance = self.get_object(user_id)
        if not user_instance:
            return Response(
                {"res": "Object with user pk does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserSerializer(user_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    # 5. Delete
    def delete(self, request, user_id, *args, **kwargs):
        '''
        Deletes a user given an user_id. Requires admin authentication.
        '''
        user_instance = self.get_object(user_id)
        if not user_instance:
            return Response(
                {"res": "Object with user pk does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        user_instance.delete()
        return Response(
            {"res": "Object deleted!"},
            status=status.HTTP_200_OK
        )
class SeriesListApiView(APIView):
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]
    serializer_class = SeriesSerializer

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        Retrieves series list. No authentication is needed.
        '''
        series_list = Series.objects.all()
        title = request.query_params.get('title', None)
        author = request.query_params.get('author', None)
        year = request.query_params.get('year', None)
        params = {"title":title,"author":author,"year":year}

        for key,value in params.items():
            if value is not None:
                series_list = series_list.filter(**{key:value})

        rating = request.query_params.get('rating[gte]', None)
        if rating is not None:
            series_list = series_list.filter(rating__gte=rating)
       
        serializer = SeriesSerializer(series_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 2. Create
    # @swagger_auto_schema(request_body=SeriesSerializer)
    def post(self, request, *args, **kwargs):
        '''
        Creates a new series. Requires authentication.
        '''
        # request.data["reviews"] = []
        serializer = SeriesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewListApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ReviewSerializer

    # 1. List all
    def get(self, request, series_pk, *args, **kwargs):
        '''
        Retrieves reviews list. No authentication is needed. 
        '''
        # reviews = Review.objects.all()
        series = Series.objects.get(pk=series_pk)
        reviews = Review.objects.filter(series=series)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 2. Create
    # @swagger_auto_schema(request_body=ReviewSerializer)
    def post(self, request, series_pk, *args, **kwargs):

        '''
        Creates a new review given a series_id. Requires authentication.
        '''
        # data = {
        #     'content': request.data.get('content'), 
        #     'rating': request.data.get('rating'), 
        # }
        series = Series.objects.get(pk=series_pk)

        review_list = series.reviews.all()
        for review in review_list:
            if review.reviewer == request.user:
                return Response(
                    {"res": "You can't review a series more than once"}, 
                    status=status.HTTP_400_BAD_REQUEST
                ) 
    
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reviewer=request.user,series=series)
            series.update()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SeriesDetailApiView(APIView):
    
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, series_pk):
        '''
        Helper method to get the object with given series_id
        '''
        try:
            return Series.objects.get(pk=series_pk)
        except Series.DoesNotExist:
            return None
  
    # 3. Retrieve
    def get(self, request, series_pk, *args, **kwargs):
        '''
        Retrieves a series details given a series_id. No authentication is needed.
        '''       
        series_instance = self.get_object(series_pk)
        if not series_instance:
            return Response(
                {"res": "Series does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SeriesSerializer(series_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 4. Update
    # @swagger_auto_schema(request_body=SeriesSerializer)
    def put(self, request, series_pk, format=None,*args, **kwargs,):
        '''
        Updates a series details given a series_id. Requires authentication.
        '''
        series_instance = self.get_object(series_pk)
        if not series_instance:
            return Response(
                {"res": "Series does not exist"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
       
        try:
            request.data.pop("reviews")
        except:
            pass
        serializer = SeriesSerializer(instance = series_instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 5. Delete
    def delete(self, request, series_pk, *args, **kwargs):
        '''
        Deletes a series given a series_id. Requires authentication.
        '''
        series_instance = self.get_object(series_pk)
        if not series_instance:
            return Response(
                {"res": "Series does not exist"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        series_instance.delete()
        return Response(
            {"res": "Series successfully deleted!"},
            status=status.HTTP_200_OK
        )

class ReviewDetailApiView(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, review_pk):
        '''
        Helper method to get the object with given a review_id
        '''
        try:
            return Review.objects.get(pk=review_pk)
        except Review.DoesNotExist:
            return None
    def review_belongs_to_series(self, review_instance, series_pk):
        '''
        Helper method to get check is a review belongs to a series, given a series_id and
        review object (instance). Returns the series object (instance) if True and None otherwise.
        '''
        series_instance=Series.objects.get(pk=series_pk)
        if review_instance.series == series_instance:
            return series_instance
        else:
            return None
    # 3. Retrieve
    def get(self, request, series_pk, review_pk, *args, **kwargs):
        '''
        Retrieves review details given a series_id and a review_id.
        Review must belong to series. Authentication is not needed.
        '''
        review_instance = self.get_object(review_pk)
        if not review_instance:
            return Response(
                {"res": "Review does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        series_instance=self.review_belongs_to_series(review_instance, series_pk)
        if not series_instance:
            return Response(
                {"res": "Review does not belong to series"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ReviewSerializer(review_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 4. Update
    # @swagger_auto_schema(request_body=ReviewSerializer)
    def put(self, request, series_pk, review_pk, format=None,*args, **kwargs,):
        '''
        Updates a review details given a series_id and a review_id.
        Review must belong to series. 
        Authentication: user must be the creator of the review.
        '''
        review_instance = self.get_object(review_pk)
        if not review_instance:
            return Response(
                {"res": "Review does not exist"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        series_instance=self.review_belongs_to_series(review_instance, series_pk)
        if not series_instance:
            return Response(
                {"res": "Review does not belong to series"},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.check_object_permissions(request, review_instance)
        
        serializer = ReviewSerializer(instance = review_instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            series_instance.update()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 5. Delete
    def delete(self, request, series_pk, review_pk, *args, **kwargs):
        '''
        Deletes a review given a series_id and a review_id.
        Review must belong to series.
        Authentication: user must be the creator of the review.
        '''
        review_instance = self.get_object(review_pk)
        if not review_instance:
            return Response(
                {"res": "Review does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        series_instance=self.review_belongs_to_series(review_instance, series_pk)
        if not series_instance:
            return Response(
                {"res": "Review does not belong to series"},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.check_object_permissions(request, review_instance)

        review_instance.delete()
        series_instance.update()

        return Response(
            {"res": "Review successfully deleted!"},
            status=status.HTTP_200_OK
        )

class ReviewLikeListApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self, review_pk):
        '''
        Helper method to get the object given a review_id
        '''
        try:
            return Review.objects.get(pk=review_pk)
        except Review.DoesNotExist:
            return None
    def review_belongs_to_series(self, review_instance, series_pk):
        '''
        Helper method to get check is a review belongs to a series, given a series_id and
        review object (instance). Returns the series object (instance) if True and None otherwise.
        '''
        series_instance=Series.objects.get(pk=series_pk)
        if review_instance.series == series_instance:
            return series_instance
        else:
            return None
    # 4. Update
    def put(self, request, series_pk,review_pk, format=None,*args, **kwargs,):
        '''
        Likes a review. Authentication is needed.
        Request body must be empty.
        '''
        review_instance = self.get_object(review_pk)
        if not review_instance:
            return Response(
                {"res": "Review does not exist"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        series_instance=self.review_belongs_to_series(review_instance, series_pk)
        if not series_instance:
            return Response(
                {"res": "Review does not belong to series"},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif request.user in review_instance.likes.all():
            return Response(
                {"res": "You have already liked this review"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        review_instance.likes.add(request.user) 
        series_instance.update()
        serializer = ReviewSerializer(review_instance)
        return Response(
            {
                "res": "Successfully liked this review!",
                # "body": serializer.data
            },
            status=status.HTTP_200_OK)

class ReviewUnlikeListApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self, review_pk):
        '''
        Helper method to get the object given a review_id
        '''
        try:
            return Review.objects.get(pk=review_pk)
        except Review.DoesNotExist:
            return None
    def review_belongs_to_series(self, review_instance, series_pk):
        '''
        Helper method to get check is a review belongs to a series, given a series_id and
        review object (instance). Returns the series object (instance) if True and None otherwise.
        '''
        series_instance=Series.objects.get(pk=series_pk)
        if review_instance.series == series_instance:
            return series_instance
        else:
            return None
    # 4. Update
    def put(self, request, series_pk,review_pk, format=None,*args, **kwargs,):
        '''
        Unlikes a review. Authentication is needed.
        Request body must be empty.
        '''
        review_instance = self.get_object(review_pk)
        if not review_instance:
            return Response(
                {"res": "Review does not exist"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        series_instance=self.review_belongs_to_series(review_instance, series_pk)
        if not series_instance:
            return Response(
                {"res": "Review does not belong to series"},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif request.user not in review_instance.likes.all():
            return Response(
                {"res": "Review not in your liked list"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        review_instance.likes.remove(request.user) 
        series_instance.update()
        serializer = ReviewSerializer(review_instance)
        return Response(
            {
                "res": "Successfully unliked this review!",
                # "body": serializer.data
            },
            status=status.HTTP_200_OK)

class LikedReviewListApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        '''
        Retrieves reviews liked by authenticated user.
        '''
        user = request.user
        series_list = user.liked
        serializer = ReviewSerializer(series_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Aditional method that replicates the "like"/"Unlike" requests from another endpoint.

    # # 2. Create
    # def put(self, request, *args, **kwargs):
    #     '''
    #     Create the Todo with given todo data
    #     '''
        
    #     if list(request.data.keys())[0] == "like":
    #         review_instance=Review.objects.get(pk=request.data["like"])
    #         if not review_instance:
    #             return Response(
    #                 {"res": "Reviewdoes not exist"}, 
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
    #         if request.user in review_instance.likes.all():
    #             return Response(
    #                 {"res": "You have already liked this review"}, 
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
    #         request.user.liked.add(review_instance)
    #         series_instance = Series.objects.get(pk=review_instance.series.pk)
    #         series_instance.update()

    #         serializer = ReviewSerializer(review_instance)
    #         return Response(
    #         {
    #             "res": "Successfully liked this review!",
    #             "body": serializer.data
    #         },
    #         status=status.HTTP_200_OK)
    #     elif list(request.data.keys())[0] == "unlike":
    #         review_instance=Review.objects.get(pk=request.data["unlike"])
    #         if not review_instance:
    #             return Response(
    #                 {"res": "Review pk does not exist"}, 
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
    #         if request.user not in review_instance.likes.all():
    #             return Response(
    #                 {"res": "Review not in your liked list"}, 
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
    #         request.user.liked.remove(review_instance)
    #         series_instance = Series.objects.get(pk=review_instance.series.pk)
    #         series_instance.update()

    #         serializer = ReviewSerializer(review_instance)
    #         return Response(
    #         {
    #             "res": "Successfully liked this review!",
    #             "body": serializer.data
    #         },
    #         status=status.HTTP_200_OK)
    #     else:
    #         return Response(
    #             {"res": "Body key must be either /like/ or /unlike/"}, 
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
