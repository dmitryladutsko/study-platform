from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Profile(models.Model):

    class Type(models.IntegerChoices):
        ADMIN = 1
        TEACHER = 2
        STUDENT = 3

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField("Отчество", max_length=32, null=True, blank=True)
    type = models.IntegerField("Тип", choices=Type.choices, null=True)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return "Профиль пользователя %s" % self.user


def create_user_profile(sender, instance, created, **kwargs):
    if created:
       profile, created = Profile.objects.get_or_create(user=instance)


post_save.connect(create_user_profile, sender=User)


class Application(models.Model):

    email = models.EmailField()
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    middle_name = models.CharField(max_length=32, null=True, blank=True)
    group_id = models.IntegerField()

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return f"{self.last_name} {self.first_name}, группа {self.group_id}"
