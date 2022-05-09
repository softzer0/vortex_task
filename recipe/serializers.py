from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from user.serializers import UserDetailsSerializer
from . import models


class SerializerWithUser(serializers.Serializer):
    user = UserDetailsSerializer(without_email=True)

    def __init__(self, *args, **kwargs):
        kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if self.context['request'].method in ('POST', 'PUT', 'PATCH'):
            self.fields['user'] = serializers.HiddenField(default=serializers.CurrentUserDefault())


class RecipeSerializer(SerializerWithUser, serializers.ModelSerializer):
    ingredients = serializers.SlugRelatedField(queryset=models.Ingredient.objects.all(), slug_field='name', many=True)
    average_rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Recipe
        fields = '__all__'


class IngredientSerializer(SerializerWithUser, serializers.ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = '__all__'

    def validate(self, attrs):
        if 'name' in attrs:
            attrs['name'] = attrs['name'].capitalize()
        if models.Ingredient.objects.filter(name=attrs['name']).exists():
            raise ValidationError(UniqueValidator.message, code='unique')
        return attrs


class RatingSerializer(SerializerWithUser, serializers.ModelSerializer):
    class Meta:
        model = models.Rating
        fields = '__all__'
        # This below is due to a bug which isn't yet solved: https://github.com/encode/django-rest-framework/issues/7173
        validators = [
            UniqueTogetherValidator(
                queryset=models.Rating.objects.all(),
                fields=('user', 'recipe'),
                message=_("You already gave rating to specified recipe.")
            )
        ]

    def validate_recipe(self, value):
        if value.user == self.context['request'].user:
            raise ValidationError(_("You cannot rate your own recipe."))
        return value

