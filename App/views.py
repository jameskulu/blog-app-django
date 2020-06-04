from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, auth
from .models import Profile, Post, Comment
from .forms import UserForm, ProfileForm, PostForm, CommentForm
from django.db.models import Q
from .decoraters import unauthenticated_user
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages


@login_required(login_url='/login')
def index(request):
    posts = Post.objects.all()
    return render(request, 'index.html', {'posts': posts, })


@login_required(login_url='/login')
def detail(request, pk):
    posts = Post.objects.get(pk=pk)
    comments = Comment.objects.filter(post=posts).order_by('-time_stamp')

    if request.method == 'POST':

        form = CommentForm(request.POST)
        if form.is_valid():
            content = request.POST.get('content')
            comment = Comment.objects.create(
                post=posts, user=request.user, content=content)
            comment.save()
            return redirect('detail-post', posts.id)
    else:
        form = CommentForm()
    is_liked = False
    if posts.likes.filter(id=request.user.id).exists():
        is_liked = True

    context = {
        'posts': posts,
        'is_liked': is_liked,
        'comments': comments,
        'form': form,
    }
    return render(request, 'detail.html', context)


@unauthenticated_user
def signup(request):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username alredy taken")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already taken")
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password, first_name=firstname, last_name=lastname)
                user.save()
                messages.success(request, "Account created successfully")
                return redirect('/login')
        else:
            messages.warning(request, "Password didn't matched")

    return render(request, 'signup.html', {})


@unauthenticated_user
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Your username/passsword is incorrect")
            return redirect('/login')
    return render(request, 'login.html', {})


def logout(request):
    auth.logout(request)
    return redirect('/login')


@login_required(login_url='/login')
def profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully")
            return redirect('/profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'profile.html', context)


@login_required(login_url='/login')
def create_post(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            obj = post_form.save(commit=False)
            obj.author = request.user
            obj.save()
            messages.success(request, 'Posted successfully')
            return redirect('/')
    else:
        post_form = PostForm()

    context = {
        'form': post_form
    }

    return render(request, 'post.html', context)


# def test_func(self):
#     post = self.get_object()
#     if self.request.user == post.author:
#         return True
#     return False


# @user_passes_test(test_func)
# def update_post(request, pk):
#     posts = Post.objects.get(pk=pk)
#     if request.method == 'POST':
#         post_update_form = PostForm(request.POST, instance=posts)
#         post_update_form.save()
#         return redirect('/')
#     else:
#         post_update_form = PostForm(instance=posts)
#     context = {
#         'post_update_form': post_update_form
#     }
#     return render(request, 'post_update.html', context)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['content', ]
    template_name = 'post.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form_valid = super().form_valid(form)
        messages.success(self.request, "Updated successfully")
        return form_valid

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


@login_required
def delete_post(request, pk):
    posts = Post.objects.get(pk=pk)
    user = request.user
    if posts.author != user:
        return HttpResponse('You are not authorized to view this page.')
    if request.method == 'POST':
        posts.delete()
        messages.error(request, "Deleted successfully")
        return redirect('/')
    context = {
        'posts': posts,
    }
    return render(request, 'delete-post.html', context)

# class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
#     model = Post
#     template_name = 'delete-post.html'
#     success_url = '/'

#     def test_func(self):
#         post = self.get_object()
#         if self.request.user == post.author:
#             return True
#         return False


def search(request):
    try:
        q = request.GET.get('q')
    except:
        q = None
    if q:
        posts = Post.objects.filter(Q(content__icontains=q) | Q(
            author__first_name__icontains=q) | Q(author__last_name__icontains=q) | Q(author__username__icontains=q))
        context = {'posts': posts, 'query': q, }
        template_name = 'search.html'
    else:
        template_name = 'index.html'
        context = {}
    return render(request, template_name, context)


def likes_func(request):
    # posts = Post.objects.get(pk=request.POST.get('like-post'))
    posts = Post.objects.get(id=request.POST.get('id'))
    is_liked = False
    if posts.likes.filter(id=request.user.id).exists():
        posts.likes.remove(request.user.id)
        is_liked = False
    else:
        posts.likes.add(request.user)
        is_liked = True
    context = {
        'posts': posts,
        'is_liked': is_liked,
    }
    if request.is_ajax():
        html = render_to_string('likes.html', context, request=request)
        return JsonResponse({'form': html})
