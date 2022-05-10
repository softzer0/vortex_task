from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from .filters import OwnFilter, RecipeFilter
from .permissions import IsOwnerOrReadOnly
from . import serializers, models


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RecipeSerializer
    queryset = models.Recipe.objects.prefetch_related('rating_set').annotate(average_rating=Avg('rating__value'))
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('name', 'text', 'ingredients__name')
    filterset_class = RecipeFilter


class IngredientViewSet(generics.ListCreateAPIView, viewsets.GenericViewSet):
    serializer_class = serializers.IngredientSerializer
    queryset = models.Ingredient.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)

    @action(methods=['GET'], url_path='top', detail=False)
    def get_top_5(self, request):
        queryset = self.filter_queryset(self.get_queryset())\
                    .annotate(recipe_count=Count('recipe')).order_by('-recipe_count')[:5]
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RatingSerializer
    queryset = models.Rating.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OwnFilter

