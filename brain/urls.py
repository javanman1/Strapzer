from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('settings', views.settings, name='settings'),
    path('upload', views.upload, name='upload'),
    path('follow', views.follow, name='follow'),
    path('search', views.search, name='search'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('like-post', views.like_post, name='like-post'),
    # path('delete-post/<int:post_id>/', views.delete_post, name='delete-post'),
    # path('edit-post/<int:post_id>/', views.edit_post, name='edit-post'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('add_comment/<str:username>/', views.add_comment, name='add_comment'),
    # path('send-message/<str:recipient>/', views.send_message, name='send-message'),
    # path('notifications', views.notifications, name='notifications'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
]