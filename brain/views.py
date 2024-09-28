from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount, Comment, Chat
# from .models import Notification, Message, Conversation
from itertools import chain
import google.generativeai as genai
import random, requests, openai
from django.utils import timezone
# Create your views here.



@login_required(login_url='signin')
def  index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    #Retrieve comments for each post
    post_comments = {}
    for post in feed_list:
        comments_with_profile = []
        comments = Comment.objects.filter(post=post)
        for comment in comments:
            comment_profile = Profile.objects.get(user=comment.user)
            
            comments_with_profile.append((comment, comment_profile.profileimg.url))
            post_comments[post.id] = comments_with_profile

    #user suggestion starts
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    return render(request,'index.html', {'user_profile': user_profile, 'posts':feed_list, 'post_comments': post_comments, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})

@login_required(login_url='signin')
def upload(request):

    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
 
    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)
 
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes+1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes-1
        post.save()
        return redirect('/')

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        print('user: '+user)
        print('follower: '+follower)
        
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)

    else:
        return redirect('/')

@login_required(login_url='signin')
def add_comment(request, username):
    if request.method == 'POST':
        user = request.user
        post_id = request.POST.get('post_id')
        content = request.POST.get('content')
        commenter = User.objects.get(username=username)

        post = Post.objects.get(id=post_id)

        #Create a new comment
        comment = Comment.objects.create(post=post, text=content, user=user)
        comment.save()

        user_profile = Profile.objects.get(user=user)
        return redirect('/')
        Notification.objects.create(user=post.user, content=f'{request.user.username} commented on your post.')
    else:
        return redirect('/')

openai_api_key = 'input-your-key'
openai.api_key = openai_api_key
genai.configure(api_key="AIzaSyAvHNBwZ2afilLoJBCVTFGLcwrMK4eXfyo")

# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_NONE"
  },
]
# Set up the model
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
    }

model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

convo = model.start_chat(history=[
    {
        "role": "user",
        "parts": ["Hello"]
    },
    {
        "role": "model",
        "parts": ["Hi there! How can I help you today?"]
    },
    {
        "role": "user",
        "parts": ["Can you help me for my history assignment?"]
    },
    {
        "role": "model",
        "parts": ["Sure, I can help you with your history assignment. What is the topic of your assignment? \n\nHere are some general tips for completing a history assignment: \n\n* **Start by understanding the assignment.** Make sure you know what the professor is asking you to do. Read the assignment instructions carefully and ask questions if you don't understand something.\n* **Do your research.** Gather information from a variety of sources, including books, articles, and websites. Be sure to evaluate the credibility of your sources before using them in your assignment.\n* **Organize your thoughts.** Before you start writing, take some time to organize your thoughts. This will help you write a clear and concise assignment.\n* **Write a strong thesis statement.** Your thesis statement is the main argument of your assignment. It should be specific, arguable, and supported by evidence.\n* **Use evidence to support your claims.** Don't just make assertions; back up your claims with evidence from your research.\n* **Proofread your work.** Once you've finished writing your assignment, take some time to proofread it carefully. Make sure there are no errors in grammar, spelling, or punctuation.\n\n**Here are some additional resources that may be helpful:**\n\n* [How to Write a History Paper](https://www.history.ucsb.edu/faculty/marcuse/130b/130B_Essays.htm#Writing)\n* [The History Essay](https://www.csun.edu/~hcdrh/historyessay.html)\n* [Writing History Papers](https://www.liu.edu/cwis/cwp/library/workshop/writehist.htm)\n\n**I can also help you with specific questions about your assignment. Just let me know what you need help with.**"]
    },
    {
        "role": "user",
        "parts": ["Who discovered america"]
    },
    {
        "role": "model",
        "parts": ["**Christopher Columbus** is credited with discovering America in 1492. He was an Italian explorer who sailed across the Atlantic Ocean under the sponsorship of the Spanish crown. Columbus made four voyages to the Americas, and his explorations opened the way for European colonization of the New World.\n\nHowever, it is important to note that there is evidence that other people may have reached the Americas before Columbus. For example, there is evidence that Vikings from Greenland visited North America around 1000 AD. Additionally, there is some evidence that Chinese explorers may have reached the Americas even earlier than the Vikings.\n\nNonetheless, Columbus's voyages had a profound impact on the history of the Americas. His explorations led to the establishment of permanent European settlements in the New World, and they also sparked a wave of European exploration and colonization that would continue for centuries to come.\n\nHere is a timeline of some of the key events in the European exploration of the Americas:\n\n* **1000 AD:** Vikings from Greenland visit North America.\n* **1492:** Christopher Columbus sails across the Atlantic Ocean and reaches the Bahamas.\n* **1493:** Columbus returns to the Americas and explores the Caribbean islands.\n* **1497:** John Cabot explores the coast of North America.\n* **1513:** Vasco Núñez de Balboa crosses the Isthmus of Panama and becomes the first European to see the Pacific Ocean.\n* **1519:** Ferdinand Magellan leads the first expedition to circumnavigate the globe.\n* **1521:** Hernán Cortés conquers the Aztec Empire in Mexico.\n* **1532:** Francisco Pizarro conquers the Inca Empire in Peru.\n\nBy the end of the 16th century, Europeans had established permanent settlements in North and South America. These settlements would eventually grow into the United States, Canada, Mexico, and other countries."]
    },
    ])
#def ask_openai(message):
        # response = openai.ChatCompletion.create(
        #     model = "gpt-4",
        #     messages=[
        #         {"role": "system", "content": "You are an helpful assistant."},
        #         {"role": "user", "content": message},
        #     ]
        # )
        
        # answer = response.choices[0].message.content.strip()
        # return answer

# Create your views here.
@login_required(login_url='signin')
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        response = model.generate_content(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats})
        

# @login_required(login_url='signin')
# def delete_post(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     if request.method == 'POST' and post.user == request.user:
#         post.delete()
#         return redirect('/')
#     else:
#         return redirect('/')

# @login_required(login_url='signin')
# def edit_post(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     if request.method == 'POST' and post.user == request.user:
#         caption = request.POST.get('caption')
#         if caption:
#             post.caption = caption
#             post.save()
#         return redirect('/')
#     else:
#         return redirect('/')

# @login_required(login_url='signin')
# def send_message(request, username):
#     receiver = get_object_or_404(User, username=username)
#     if request.method == 'POST':
#         text = request.POST.get('text')
#         if text:
#             message = Message.objects.create(sender=request.user, receiver=receiver, text=text)
#             message.save()
#             #Added option to send notification about new message    
#     Notification.objects.create(user=receiver, content=f'{request.user.username} sent you a message.')
#     return redirect('/')

# def notifications(request):
#     notifications = Notification.objects.filter(user=request.user, viewed=False)
#     return render(request, 'notifications.html', {'notifications':notifications})

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':

        if request.FILES.get('image') == None:
            image = request.FILES.get('image', user_profile.profileimg)
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        return redirect('settings')


    return render(request, 'setting.html', {'user_profile': user_profile})

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken Sempai')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken Sempai')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password Not Matching sensei')
            return redirect('signup')
    else: 
        return render(request, 'signup.html')

def signin(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')

    else:
        return render(request, 'signin.html')


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')