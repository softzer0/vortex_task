from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return '#%d: %s' % (self.pk, self.name)


class Recipe(models.Model):
    name = models.CharField(max_length=256)
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient)

    def __str__(self):
        return '#%d: %s' % (self.pk, self.name)

