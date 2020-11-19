from django.db import models


class Title(models.Model):
    title = models.CharField(max_length=500)


class Data(models.Model):
    article = models.CharField(max_length=30)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    content = models.CharField(max_length=1000)


class Question(models.Model):
    knowledge_data = models.ForeignKey(Data, on_delete=models.CASCADE)
    content = models.CharField(max_length=1000)
