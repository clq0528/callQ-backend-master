from .serializers import GoodsSerializer,CategorySerializer,BannerSerializer,HotSearchSerializer,IndexCategorySerializer
from rest_framework.views import APIView
from rest_framework.views import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework.throttling import UserRateThrottle,AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .filters import GoodsFilter
from rest_framework.authentication import TokenAuthentication

from .models import Goods,GoodsCategory,Banner,HotSearchWords
# Create your views here.


# # class GoodsListView(APIView):
#     """
#     List goods
#     """
    # def get(self, request, format=None):
    #     goods = Goods.objects.all()[:10]
    #     goods_serializer = GoodsSerializer(goods, many=True)
    #     return Response(goods_serializer.data)

    # def post(self, request, format=None):
    #     serializer = GoodsSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GoodsPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100

# class GoodsListView(generics.ListAPIView):
#     queryset = Goods.objects.all()
#     serializer_class = GoodsSerializer
#     pagination_class = GoodsPagination

class GoodsListViewSet(CacheResponseMixin,mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    """
    商品列表
    """
    throttle_classes = (AnonRateThrottle,)
    queryset = Goods.objects.all().order_by('id')
    serializer_class = GoodsSerializer
    pagination_class = GoodsPagination
    # authentication_classes = (TokenAuthentication,)
    filter_backends = (DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter)
    filter_class = GoodsFilter
    # filter_fields = ('name', 'goods_num')
    search_fields = ('name','goods_brief','goods_desc')
    ordering_fields = ('sold_num','shop_price')
    #点击数功能
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class CategoryViewSet(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    """
    list:
        商品分类列表数据
    retrieve:
        获取商品分类详情
    """
    queryset = GoodsCategory.objects.all().order_by('id')
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = CategorySerializer

class BannerViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    """
    list:
        Banner列表数据
    """
    queryset = Banner.objects.all().order_by('index')
    serializer_class = BannerSerializer

class HotSearchViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    """
    list:
        Banner列表数据
    """
    queryset = HotSearchWords.objects.all().order_by('index')
    serializer_class = HotSearchSerializer


class IndexCategoryViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    """
    list:
        首页商品分类数据
    """
    queryset = GoodsCategory.objects.filter(is_tab=True,name__in=["生鲜食品","酒水饮料"])
    # queryset = GoodsCategory.objects.filter(is_tab=True)
    serializer_class = IndexCategorySerializer