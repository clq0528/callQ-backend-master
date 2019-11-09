"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path
from django.conf.urls import url,include
import xadmin
from backend.settings import MEDIA_ROOT
from django.views.static import serve

from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
# from goods.views_base import GoodsListView
# from goods.views import GoodsListView,GoodsListViewSet
from goods.views import GoodsListViewSet,CategoryViewSet,BannerViewSet,HotSearchViewSet,IndexCategoryViewSet
from user.views import SmsCodeViewset,UserViewset
from user_operation.views import UserFavViewset,LeavingMessageViewset,AddressViewset
from trade.views import ShoppingCartViewset,OrderViewset
from rest_framework_jwt.views import obtain_jwt_token


router = DefaultRouter()
router.register(r'goods', GoodsListViewSet,base_name="goods")
router.register(r'categorys', CategoryViewSet,base_name="categorys")
router.register(r'code', SmsCodeViewset,base_name="code")
router.register(r'users', UserViewset,base_name="users")
router.register(r'userfavs', UserFavViewset,base_name="userfavs")
router.register(r'messages', LeavingMessageViewset,base_name="messages")
router.register(r'address', AddressViewset,base_name="address")
router.register(r'shopcarts', ShoppingCartViewset,base_name="shopcarts")
router.register(r'orders', OrderViewset,base_name="orders")
router.register(r'banners', BannerViewSet,base_name="banners")
router.register(r'hotsearchs', HotSearchViewSet,base_name="hotsearchs")
router.register(r'indexgoods', IndexCategoryViewSet,base_name="indexgoods")

# goods_list = GoodsListViewSet.as_view({
#     'get':'list',
# })
def trigger_error(request):
    division_by_zero = 1 / 0

from trade.views import AlipayView
from django.views.generic import TemplateView
urlpatterns = [
    # path('admin/', admin.site.urls),
    url(r'^xadmin/',xadmin.site.urls),
    path('ueditor/', include('DjangoUeditor.urls')),
    url(r'^media/(?P<path>.*)$',serve,{"document_root":MEDIA_ROOT}),
    # url(r'goods/$',GoodsListView.as_view(),name="goods-list"),
    url(r'^', include(router.urls)),
    url(r'docs/',include_docs_urls(title='商城后端')),
    url(r'^api-auth/',include('rest_framework.urls')),
    #drf 自带token认证模式
    url(r'^api-token-auth/', views.obtain_auth_token),
    #jwt认证模式
    url(r'^login/$', obtain_jwt_token),

    #测试sentry
    path('sentry-debug/', trigger_error),

    url(r'^index/',TemplateView.as_view(template_name="index.html"),name="index"),
    url(r'^alipay/return/', AlipayView.as_view(),name="alipay"),
    #第三方登入
    url('', include('social_django.urls', namespace='social')),
]
