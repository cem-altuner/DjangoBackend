from django.contrib import admin
from django.urls import path, include, re_path

# This is very important
from .models import Customer as User
from .views import *
from django.conf import settings

# this is for Token Auth
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth import views as auth_views
from rest_framework import routers
from django.conf.urls.static import static

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
#router.register('customers', UserViewSet)
router.register('companies', CompanyViewSet)

#router.register('products', ProductViewSet)
router.register('catalogs', CatalogViewSet)
#router.register('shopping-list', ShoppingListViewSet)
router.register('shopping-list-items', ShoppingListItemViewSet)

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
                  path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
                  path('api/', include(router.urls)),
                  path('api/shopping-list/', ShoppingListApiView.as_view()),
                  
                  path('api/customers/', UserApiView.as_view()),
                  path('', HomepageView.as_view()),
                  path('signup/', signup),
                  re_path(
                      r'activate-account/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
                      activate_account, name='activate_account'),
                  path(r'password_reset/',
                       PasswordResetView.as_view(template_name='admin/password_reset_form.html'),
                       name='password_reset'),
                  path(r'password_reset/done/',
                       auth_views.PasswordResetDoneView.as_view(template_name='admin/password_reset_done.html'),
                       name='password_reset_done'),
                  re_path(r'reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
                          auth_views.PasswordResetConfirmView.as_view(
                              template_name='admin/password_reset_confirm.html'), name='password_reset_confirm'),
                  path(r'reset/done/',
                       auth_views.PasswordResetCompleteView.as_view(template_name='admin/password_reset_complete.html'),
                       name='password_reset_complete'),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
