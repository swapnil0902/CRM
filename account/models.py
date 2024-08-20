from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField(
        Group,
        related_name='account_user_groups',  # Custom related name to avoid clash
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='account_user_permissions',  # Custom related name to avoid clash
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

@receiver(post_save, sender=settings.AUTH_USER_MODEL) 
def createAuthToken(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user = instance)


@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def delete_user_token(sender, instance, **kwargs):
    Token.objects.filter(user=instance).delete()
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import Group
from .forms import GroupForm

def group_list(request):
    groups = Group.objects.all()
    return render(request, 'group_list.html', {'groups': groups})

def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            return redirect('group_list')
    else:
        form = GroupForm()
    return render(request, 'group_form.html', {'form': form})

def group_update(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_list')
    else:
        form = GroupForm(instance=group)
    return render(request, 'group_form.html', {'form': form})

def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        return redirect('group_list')
    return render(request, 'group_confirm_delete.html', {'group': group})
