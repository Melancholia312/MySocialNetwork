from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import RegistrationForm, LoginForm, CommentForm, PostForm, SettingsForm
from .models import SpecificUser, Follower, Post, Comment
from django import views
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView, BaseUpdateView
from django.http import HttpResponseForbidden
from django.db.models import Count


class BaseView(LoginRequiredMixin, views.generic.ListView):
    login_url = 'login'
    model = Post
    template_name = 'base.html'
    context_object_name = 'posts'
    paginate_by = 3

    def get_queryset(self):
        user = self.request.user
        current_user_posts = []
        followings_list = Follower.objects.filter(subscriber=user)
        for owner in followings_list:
            owner_posts = Post.objects.filter(user=owner.user)
            for post in owner_posts:
                current_user_posts.append(post)
        current_user_posts.sort(key=lambda post: post.create_date, reverse=True)
        return current_user_posts


class LoginView(views.View):

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, 'login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(request, 'login.html', context)


class RegistrationView(views.View):

    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, 'registration.html', context)

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.gender = form.cleaned_data['gender']
            new_user.birthday = form.cleaned_data['birthday']
            new_user.bio = form.cleaned_data['bio']
            new_user.phone = form.cleaned_data['phone']
            new_user.avatar = form.cleaned_data['avatar']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect('/')
        context = {
            'form': form
        }
        return render(request, 'registration.html', context)


class LogoutView(views.View):

    def get(self, request):
        logout(request)
        return redirect('/')


class ProfileListView(LoginRequiredMixin, views.generic.ListView):
    login_url = 'login'
    model = SpecificUser
    template_name = 'social/profiles.html'
    context_object_name = 'profiles'
    paginate_by = 3
    queryset = SpecificUser.objects.order_by('-date_joined')


class ProfileDetailView(LoginRequiredMixin, views.generic.DetailView):
    login_url = 'login'
    model = SpecificUser
    template_name = 'social/profile.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(user=kwargs['object'])
        return context


class Follow(LoginRequiredMixin, views.View):

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            owner = SpecificUser.objects.filter(id=kwargs['pk']).first()
            is_follow = Follower.objects.filter(subscriber=request.user, user=owner).exists()
            if not is_follow:
                follower = request.user
                if follower != owner:
                    Follower.objects.create(user=owner, subscriber=follower)
                    messages.add_message(request, messages.INFO, f'Вы успешно подписались на {owner.username}')
                else:
                    messages.add_message(request, messages.INFO, f'Вы не можете подписаться сами на себя')
            else:
                messages.add_message(request, messages.INFO, f'Вы уже подписаны на {owner.username}')
        return redirect('profile', pk=kwargs['pk'])


class PostDetailView(LoginRequiredMixin, views.generic.DetailView):
    login_url = 'login'
    model = Post
    template_name = 'social/post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(post=kwargs['object'])
        return context


class AddComment(LoginRequiredMixin, views.View):

    def post(self, request, pk):
        form = CommentForm(request.POST)
        post = Post.objects.get(id=pk)
        if form.is_valid():
            form = form.save(commit=False)
            if request.POST.get("parent", None):
                form.parent_id = int(request.POST.get('parent'))
            form.post = post
            form.user = request.user
            form.save()
        return redirect(post.get_absolute_url())


class PostCreate(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Post
    fields = ('title', 'text',)

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
        return redirect('post_detail', pk=form.id)


class PostDelete(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = Post

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = self.object.user
        if user == request.user:
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def get_success_url(self):
        return reverse_lazy('profile', args=[self.request.user.id])


class PostUpdate(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Post
    fields = ('title', 'text',)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = self.object.user
        if user == request.user:
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()


class ProfileSettingsUpdate(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = SpecificUser
    form_class = SettingsForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        id = self.object.id
        if id == request.user.id:
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()


class CommentDelete(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = Comment

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = self.object.user
        if user == request.user:
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def get_success_url(self):
        return reverse_lazy('post_detail', args=[self.object.post_id])