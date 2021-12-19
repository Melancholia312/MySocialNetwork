from django.urls import path
from .views import RegistrationView, BaseView, LogoutView, LoginView, \
    ProfileDetailView, Follow, ProfileListView, PostDetailView, AddComment, PostCreate, PostDelete, PostUpdate, \
    ProfileSettingsUpdate, CommentDelete

urlpatterns = [
    path('', BaseView.as_view(), name='base'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('follow/<int:pk>/', Follow.as_view(), name='follow'),
]

urlpatterns += [
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile'),
    path('profiles/', ProfileListView.as_view(), name='profiles'),
    path('profile/<int:pk>/settings/', ProfileSettingsUpdate.as_view(), name='settings'),

]

urlpatterns += [
    path('comment/<int:pk>/', AddComment.as_view(), name='add_comment'),
    path('comment/<int:pk>/delete/', CommentDelete.as_view(), name='comment_delete'),
]

urlpatterns += [
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/create/', PostCreate.as_view(), name='post_create'),
    path('post/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('post/<int:pk>/update/', PostUpdate.as_view(), name='post_update'),
]

