from chat.models import Chat
from chat.serializers import ChatSerializer
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from email.message import EmailMessage
from follow.models import Follow
from follow.serializers import FollowSerializer
from guardian.shortcuts import assign_perm
from guardian.shortcuts import get_objects_for_user
from hashtag.models import Hashtag
from hashtag.serializers import HashtagSerializer
from like.models import Like
from permissions.services import APIPermissionClassFactory
from post.models import Post
from post.serializers import PostSerializer
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from searchedHashtag.models import SearchedHashtag
from searchedHashtag.serializers import SearchedHashtagSerializer
from searchedUser.models import SearchedUser
from searchedUser.serializers import SearchedUserSerializer
from story.models import Story
from story.serializers import StorySerializer
from topic.models import Topic
from topic.views import getTrending
from versus.models import Versus
from versus.serializers import VersusSerializer
from versus.views import get_element_random, pick_post, getComments
from viewedStory.models import ViewedStory
from viewedStory.serializers import ViewedStorySerializer
from votarkUser.models import VotarkUser
from votarkUser.serializers import VotarkUserSerializer
from vote.models import Vote
import os 
import random
import smtplib
import uuid
from guardian.shortcuts import assign_perm, get_users_with_perms


EMAIL_ADRESS = 'votark.socialnet@gmail.com'
EMAIL_PASSWORD = os.environ.get('PASSWORD')

def evaluate(user, obj, request):
    return user.username == obj.username

def getVersus(user):
    post = None
    done = False
    returning = None
    while(done==False):
        while(post==None):
            choose = random.randint(0,10)
            if(choose<6):               
                index = 0
                order = {}
                valid_posts = []
                orderby = '-date'                                                           #75% new posts will be returned
                if(random.randint(0,4)==0):
                    orderby = '-order'                                                     #25% trending will be returned
                for post in Post.objects.order_by(orderby):
                    value = index
                    for following in Follow.objects.filter(follower=user).order_by('-date'):
                        if(post.user==following):
                            if(len(SearchesUser.objects.filter(searchedUser=following, user=user))==0):          #User has not searched him
                                value+=10
                            else:
                                value-=5*len(SearchesUser.objects.filter(searchedUser=following, user=user))     #This will make users with more searches come first
                    valid_posts.append(post)
                    order[index] = value
                    index+=1
                post=get_element_random(valid_posts,order)
            elif(choose>=6 and choose<10):                                                 #40% of the times it will choose from trending
                trending = getTrending(20)
                trend = random.choice(trending)
                topic = Topic.objects.filter(id=trend['topic'])[0]
                post = pick_post(topic)
        newPost = None
        while(newPost==None):
            newPost = pick_post(post.topic)
            if(newPost.id==post.id and ((newPost.image!=None and post.image!=None) or (newPost.video!=None and post.video!=None))):
                newPost=None
        if(len(Versus.objects.filter(post1=post, post2=newPost))==0):
            versus = Versus(post1=post, post2=newPost)
            versus.save()
            data = VersusSerializer(versus).data
            returning =  (data)
            done = True
        versus = Versus.objects.filter(post1=post, post2=newPost)[0]
        data = VersusSerializer(versus).data
        returning = (data)
        done = True
        """if(len(Vote.objects.filter(versus=versus))!=0):                        #This is useful when you have millions of publications
            data = VersusSerializer(versus).data
            returning = (data)
            done = True"""
    return returning

class VotarkUserViewSet(viewsets.ModelViewSet):
    queryset = VotarkUser.objects.all()
    serializer_class = VotarkUserSerializer
    permission_classes = (
        APIPermissionClassFactory(
            name='EventPermission',
            permission_configuration={
                'base': {
                    'create': True,
                    'list': True,
                },
                'instance': {
                    'chats':evaluate,
                    'destroy': evaluate,
                    'followers': True,
                    'following': True,
                    'mystories':True,
                    'partial_update': evaluate,
                    'pick': True,
                    'posts': True,
                    'restore_password': True,
                    'retrieve': True,
                    'search_history_hashtag':evaluate,
                    'search_history_user':evaluate,
                    'search_hashtag': evaluate,
                    'search_user': evaluate,
                    'search_follower': True,
                    'stories': True,
                    'update': evaluate,
                    'versus': True,
                    'isfollowing': True
                }
            }
        ),
    )

    def perform_create(self, serializer):
        user = serializer.save()
        user.password = make_password(serializer.validated_data['password'])
        user.save()
        return Response(serializer.data)


    @action(detail=False, url_path='restore', methods=['post'])
    def restore_password(self, request):
        try:
            email = request.data['email']
            user = VotarkUser.objects.get(email=email)
            password = str(uuid.uuid1())
            user.password = make_password(password)
            user.save()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL_ADRESS,EMAIL_PASSWORD)
                msg = EmailMessage()
                msg['Subject'] = 'Password has been changed'
                msg['From'] = EMAIL_ADRESS
                msg['To'] = email
                msg.set_content('Hi! ' + user.first_name + ' ' + user.last_name + ' your password has been restored\nusername: ' + user.username + '\npassword: ' + password + '\n\n\n THE TEAM OF VOTARK')
                smtp.send_message(msg)
            return Response(request.data)
        except Exception as e:
            print(e)
            return Response({'detail':'email is not valid'},status=status.HTTP_400_BAD_REQUEST)
                

    @action(detail=True, methods=['get'])
    def following(self, request, pk=None):
        user = self.get_object()
        response = []
        for follower in Follow.objects.filter(user=user):
            response.append(FollowSerializer(follower).data)
        return Response(response)    

    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        user = self.get_object()
        response = []
        for follower in Follow.objects.filter(follower=user):
            response.append(FollowSerializer(follower).data)
        return Response(response)

    @action(detail=True, methods=['get'])
    def isfollowing(self, request, pk=None):
        user = self.request.user
        asking = self.get_object()
        isfollowing = len(Follow.objects.filter(follower=asking,user=user.id))!=0
        return Response({'result':isfollowing})

    @action(detail=True, methods=['get'])
    def chats(self, request, pk=None):
        user = self.get_object()
        response = []
        for chat in get_objects_for_user(user, 'chat.view_chat').order_by('-date'):
            response.append(ChatSerializer(chat).data)
        return Response(response)

    @action(detail=True, methods=['get'])
    def search_history_hashtag(self, request, pk=None):
        user = self.get_object()
        response = []
        limit = 5
        for searched in SearchedHashtag.objects.filter(user=user).order_by('-date'):
            response.append(HashtagSerializer(searched.hashtag).data)
            limit-=1
            if(limit==0):
                return Response(response)
        return Response(response)

    @action(detail=True, methods=['get'])
    def search_history_user(self, request, pk=None):
        user = self.get_object()
        response = []
        limit=5
        for searched in SearchedUser.objects.filter(user=user).order_by('-date'):
            response.append(VotarkUserSerializer(searched.searchedUser).data)
            limit-=1
            if(limit==0):
                return Response(response)
        return Response(response)

    @action(detail=True, methods=['post'])
    def search_follower(self, request):
        user = self.get_object()
        response = []
        try:
            following = VotarkUser.objects.filter(username=request.data['username'])
            for follower in Follow.objects.filter(follower=user):
                if(follower.following==following):
                    return Response({'detail': 'true'})
            return Response({'detail': 'false'})
        except:
            return Response({'detail':'username is not valid'})        
    
    @action(detail=True, methods=['post'])
    def search_user(self, request,pk=None):
        user = self.get_object()
        try:
            query = request.data['query']
            users = VotarkUser.objects.filter(username__icontains=query)
            response=[]
            limit=5
            for votarker in users:
                if(limit>0):
                    SearchedUser.objects.create(user=user, searchedUser=votarker)
                    response.append(VotarkUserSerializer(votarker).data)
                limit-=1
            return Response(response)
        except:
            return Response({'detail':'query is not valid'})

    @action(detail=True, methods=['post'])
    def search_hashtag(self, request,pk=None):
        user = self.get_object()
        try:
            query = request.data['query']
            hashtags = Hashtag.objects.filter(content__icontains=query)
            response=[]
            limit=5
            for hash in hashtags:
                if(limit>0):
                    SearchedHashtag.objects.create(hashtag=hash, user=user)
                    response.append(HashtagSerializer(hash).data)
                limit-=1
            return Response(response)
        except Exception as e:
            print(e)
            return Response({'detail':'query is not valid'})

    @action(detail=True, methods=['get'])
    def stories(self, request, pk=None):
        user = self.get_object()
        index = 0
        order = {}
        current_response = []
        for following in Follow.objects.filter(follower=user).order_by('-date'):
            subresponse = {}
            value = index
            if len(Story.objects.filter(user=following.follower))!=0:
                subresponse['user'] = following                                                          #Order them by user
                stories = []
                for story in Story.objects.filter(user=following).order_by('-date'):                     
                    story = {}           
                    story['story'] = stories.append(StorySerializer(story).data)                              
                    if (len(ViewedStory.objects.filter(story=story, user=user))==0):                  #Check if the user has not seen the story
                        story['viewed'] = False
                    else:
                        value+=100                                                                      #This will make it go to the end of the order
                        story['viewed'] = True
                    stories.append(story)
                if (len(SearchesUser.objects.filter(searchedUser=following, user=user))==0):          #User has not searched him
                    value+=30
                else:
                    value-=5*len(SearchesUser.objects.filter(searchedUser=following, user=user))     #THis will make users with more searches come first
                subresponse['stories'] = stories
                order[index] = value
                current_response.append(subresponse)
            index+=1
        order = {k: v for k, v in sorted(order.items(), key=lambda item: item[1])}                          #Sorting by value
        response = []
        for key in order:
            response.append(current_response[key])                                                      #Returning them in the specified order
        return Response(response)
    
    @action(detail=True, methods=['get'])
    def mystories(self, request, pk=None):
        user = self.get_object()
        response = []
        for story in Story.objects.filter(user=user).order_by('-date'):
            response.append(StorySerializer(story).data)
        return Response(response)

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        user = self.get_object()
        response = []
        for post in Post.objects.filter(user=user).order_by('-date'):
            response.append(PostSerializer(post).data)
        return Response(response)

    @action(detail=False, methods=['get'])
    def versus(self, request, pk=None):
        user = self.request.user
        response = []
        for i in range(0,5):
            new = getVersus(user)
            while(new in response):
                new = getVersus(user)
            response.append(new)
        return Response(response)

    @action(detail=False, methods=['post'])
    def pick(self, request, pk=None):
        try:
            done = False
            returning = None
            while(done==False):
                postid = int(request.data['postid'])
                post = Post.objects.filter(id=postid)[0]
                user = self.request.user
                newPost = None
                while(newPost==None):
                    newPost = pick_post(post.topic)
                    if(newPost.id==post.id and ((newPost.image!=None and post.image!=None) or (newPost.video!=None and post.video!=None))):
                        newPost=None
                if(len(Versus.objects.filter(post1=post, post2=newPost))==0):
                    versus = Versus(post1=post, post2=newPost)
                    data = VersusSerializer(versus).data
                    returning =  Response(data)
                    done = True
                versus = Versus.objects.filter(post1=post, post2=newPost)[0]
                if(len(Vote.objects.filter(versus=versus))==0):
                    data = VersusSerializer(versus).data
                    returning = Response(data)
                    done = True
            return returning
        except:
            return Response({'detail':'postid is not valid'})
    
