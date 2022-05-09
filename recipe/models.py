from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class ModelWithUser(models.Model):
    user = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)

    class Meta:
        abstract = True


class Ingredient(ModelWithUser):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return '#%d: %s' % (self.pk, self.name)


class Recipe(ModelWithUser):
    name = models.CharField(max_length=256)
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient)

    def __str__(self):
        return '#%d: %s' % (self.pk, self.name)


class Rating(ModelWithUser):
    value = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    recipe = models.ForeignKey('recipe.Recipe', on_delete=models.CASCADE)

    class Meta:
        constraints = (models.UniqueConstraint(fields=('user', 'recipe'), name='rating_unique'),)

