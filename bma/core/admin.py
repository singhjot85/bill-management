from bma.core.models import BaseUserModel


from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import PermissionDenied
from django.db import transaction, router
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path
from django.urls import path, reverse
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.forms import (
    AdminPasswordChangeForm,
    AdminUserCreationForm,
    UserChangeForm,
)

csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())

@admin.register(BaseUserModel)
class BaseUserModelAdmin(admin.ModelAdmin):
    add_form_template = "admin/auth/user/add_form.html"
    change_user_password_template = None #TODO
    list_display = (
        "username",
        "email",
        "country_code",
        "phonenumber",
        "is_active",
        "created",
        "modified",
    )
    list_filter = (
        "country_code",
        "is_active",
        "created",
    )
    search_fields = (
        "username",
        'suffix',
        'first_name',
        'middle_name',
        'last_name',
        "email",
        'country_code',
        "phonenumber",
    )
    ordering = ("-created",)
    readonly_fields = ( "created", "modified")

    fieldsets = (
        ("Required Fields", {
            "fields": [ "username", "password", "email"]
        }),
        ("Mandatory Important Fields", {
            "fields": [
                "suffix", 
                "first_name",
                "middle_name", 
                "last_name", 
                "country_code", 
                "phonenumber"
            ]
        }  
        ),
        ( "Status", {
            "fields": ["is_active", "is_staff", "is_superuser" ],
            "classes": ["collapse" ]
        }),
        ("Timestamps", {
            "fields": [ "created", "modified" ],
            "classes": ["collapse" ]
        }),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "usable_password", "password1", "password2"),
            },
        ),
    )
    form = UserChangeForm
    add_form = AdminUserCreationForm
    change_password_form = AdminPasswordChangeForm

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_urls(self):
        return [
            path(
                "<id>/password/",
                self.admin_site.admin_view(self.user_change_password),
                name="auth_user_password_change",
            ),
        ] + super().get_urls()

    def lookup_allowed(self, lookup, value, request=None):
        # Don't allow lookups involving passwords.
        return not lookup.startswith("password") and super().lookup_allowed(
            lookup, value, request
        )
    
    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=""):
        user = self.get_object(request, unquote(id))
        if not self.has_change_permission(request, user):
            raise PermissionDenied
        if user is None:
            raise Http404(
                _("%(name)s object with primary key %(key)r does not exist.")
                % {
                    "name": self.opts.verbose_name,
                    "key": escape(id),
                }
            )
        if request.method == "POST":
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                # If disabling password-based authentication was requested
                # (via the form field `usable_password`), the submit action
                # must be "unset-password". This check is most relevant when
                # the admin user has two submit buttons available (for example
                # when Javascript is disabled).
                valid_submission = (
                    form.cleaned_data["set_usable_password"]
                    or "unset-password" in request.POST
                )
                if not valid_submission:
                    msg = gettext("Conflicting form data submitted. Please try again.")
                    messages.error(request, msg)
                    return HttpResponseRedirect(request.get_full_path())

                user = form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                if user.has_usable_password():
                    msg = gettext("Password changed successfully.")
                else:
                    msg = gettext("Password-based authentication was disabled.")
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect(
                    reverse(
                        "%s:%s_%s_change"
                        % (
                            self.admin_site.name,
                            user._meta.app_label,
                            user._meta.model_name,
                        ),
                        args=(user.pk,),
                    )
                )
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {"fields": list(form.base_fields)})]
        admin_form = admin.helpers.AdminForm(form, fieldsets, {})

        if user.has_usable_password():
            title = _("Change password: %s")
        else:
            title = _("Set password: %s")
        context = {
            "title": title % escape(user.get_username()),
            "adminForm": admin_form,
            "form_url": form_url,
            "form": form,
            "is_popup": (IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET),
            "is_popup_var": IS_POPUP_VAR,
            "add": True,
            "change": False,
            "has_delete_permission": False,
            "has_change_permission": True,
            "has_absolute_url": False,
            "opts": self.opts,
            "original": user,
            "save_as": False,
            "show_save": True,
            **self.admin_site.each_context(request),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.change_user_password_template
            or "admin/auth/user/change_password.html",
            context,
        )

    @sensitive_post_parameters_m
    @csrf_protect_m
    def add_view(self, request, form_url="", extra_context=None):
        if request.method in ("GET", "HEAD", "OPTIONS", "TRACE"):
            return self._add_view(request, form_url, extra_context)

        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._add_view(request, form_url, extra_context)

    def _add_view(self, request, form_url="", extra_context=None):
        # It's an error for a user to have add permission but NOT change
        # permission for users. If we allowed such users to add users, they
        # could create superusers, which would mean they would essentially have
        # the permission to change users. To avoid the problem entirely, we
        # disallow users from adding users if they don't have change
        # permission.
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful
                # error message.
                raise Http404(
                    'Your user does not have the "Change user" permission. In '
                    "order to add users, Django requires that your user "
                    'account have both the "Add user" and "Change user" '
                    "permissions set."
                )
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        username_field = self.opts.get_field(self.model.USERNAME_FIELD)
        defaults = {
            "auto_populated_fields": (),
            "username_help_text": username_field.help_text,
        }
        extra_context.update(defaults)
        return super().add_view(request, form_url, extra_context)

    def response_add(self, request, obj, post_url_continue=None):
        """
        Determine the HttpResponse for the add_view stage. It mostly defers to
        its superclass implementation but is customized because the User model
        has a slightly different workflow.
        """
        if "_addanother" not in request.POST and IS_POPUP_VAR not in request.POST:
            request.POST = request.POST.copy()
            request.POST["_continue"] = 1
        return super().response_add(request, obj, post_url_continue)