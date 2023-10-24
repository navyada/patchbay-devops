""" Django Admin customizations"""

from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from core import models


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = models.User
        fields = ('email', 'first_name', 'last_name', 'phone_number')

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users"""
    ordering = ['id']
    list_display = ['email', 'first_name', 'last_name', 'phone_number']
    fieldsets = (
        (None, {'fields': ('email', 'first_name',
                           'last_name', 'phone_number', 'password')}),
        (
            _('Permissions'),
            {'fields':
             (
                 'is_active',
                 'is_staff',
                 'is_superuser'
             )}
        ),
        (
            _('Important dates'), {'fields': ('last_login',)}
        )
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {'classes': ('wide',),
                'fields': (
                    'email',
                    'password1',
                    'password2',
                    'first_name',
                    'last_name',
                    'phone_number',
                    'is_active',
                    'is_staff',
                    'is_superuser',

                )}
         ),
    )


admin.site.register(models.User, UserAdmin)
admin.site.unregister(Group)
