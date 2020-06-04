from .models import Profile, Post, Comment
from django import forms
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'likes']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', ]
