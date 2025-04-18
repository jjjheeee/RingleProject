# study/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import TutorClass, StudentClass

@receiver(post_save, sender=StudentClass)
def update_tutorclass_true(sender, instance, created, **kwargs):
    if created:
        tutor_class = instance.tutor_class
        tutor_class.status = True
        tutor_class.save()

@receiver(post_delete, sender=StudentClass)
def update_tutorclass_flase(sender, instance, **kwargs):
    tutor_class = instance.tutor_class
    tutor_class.status = False
    tutor_class.save()

