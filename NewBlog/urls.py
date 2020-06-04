from django.contrib import admin
from django.urls import path
from App import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('create-post/', views.create_post, name='create-post'),
    path('post/<int:pk>/', views.detail, name='detail-post'),
    # path('post/<int:pk>/update/', views.update_post, name='update-post'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='update-post'),
    # path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete-post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete-post'),
    path('s/', views.search, name='search'),
    path('like/', views.likes_func, name="likes"),

    # Password
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name="password/password_reset.html"), name="password_reset"),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name="password/password_reset_done.html"), name="password_reset_done"),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="password/password_reset_confirm.html"), name="password_reset_confirm"),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name="password/password_reset_complete.html"), name="password_reset_complete"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
