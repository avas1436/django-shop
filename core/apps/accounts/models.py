# core/apps/accounts/models.py

import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounts.validators import validate_iranian_cellphone_number


# میتوان هم از عدد و هم از رشته برای تعیین نام استفاده کرد
class UserType(models.IntegerChoices):
    customer = 1, _("customer")
    admin = 2, _("admin")
    superuser = 3, _("superuser")


class UserManager(BaseUserManager):
    """
    Custom user model manager where phone_number is the unique identifier
    for authentication instead of username.
    """

    def create_user(self, phone_number, password=None, **extra_fields):
        """
        Create and save a User with the given phone number.
        Password is optional — OTP-only accounts are allowed.
        """
        if not phone_number:
            raise ValueError(_("The phone number must be set"))

        user = self.model(phone_number=phone_number, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        """
        Create and save a SuperUser with the given phone number and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("type", UserType.superuser.value)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        if not password:
            raise ValueError(_("Superuser must have a password."))

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        validators=[validate_iranian_cellphone_number],
    )
    email = models.EmailField(_("email address"), unique=True, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(
        default=False, help_text=_("Phone number verified via OTP")
    )
    type = models.IntegerField(
        choices=UserType.choices, default=UserType.customer.value
    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.phone_number

    @property
    def has_usable_password_set(self) -> bool:
        """Whether the user set a password (vs. OTP-only account)."""
        return self.has_usable_password()


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to="profile/", default="profile/default.png")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")

    def __str__(self):
        return str(self.get_fullname())

    def get_fullname(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return _("کاربر جدید")


# یک سیگنال که بعد از ساخته شدن هر کاربر یک پروفایل هم برای او ایجاد میکند
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# ==========================
# OTP
# ==========================
class OTPPurpose(models.TextChoices):
    register = "register", _("Register")
    login = "login", _("Login")
    reset_password = "reset_password", _("Reset password")
    change_phone = "change_phone", _("Change phone number")


class OTP(models.Model):
    """
    One-Time Password sent via SMS for verifying a phone number.
    """

    CODE_LENGTH = 5
    EXPIRY_MINUTES = 2
    MAX_ATTEMPTS = 5
    RESEND_COOLDOWN_SECONDS = 60

    phone_number = models.CharField(
        max_length=15, validators=[validate_iranian_cellphone_number]
    )
    code = models.CharField(max_length=8)
    purpose = models.CharField(max_length=20, choices=OTPPurpose.choices)

    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)

    created_date = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = _("OTP")
        verbose_name_plural = _("OTPs")
        indexes = [
            models.Index(fields=["phone_number", "purpose", "is_used"]),
        ]

    def __str__(self):
        return f"{self.phone_number} - {self.purpose}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=self.EXPIRY_MINUTES)
        super().save(*args, **kwargs)

    @staticmethod
    def generate_code() -> str:
        return "".join(random.choices("0123456789", k=OTP.CODE_LENGTH))

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        return (
            not self.is_used
            and not self.is_expired
            and self.attempts < self.MAX_ATTEMPTS
        )

    @classmethod
    def create_for(cls, phone_number: str, purpose: str) -> "OTP":
        """
        Create a fresh OTP, invalidating any previous unused ones
        for the same phone_number + purpose.
        """
        cls.objects.filter(
            phone_number=phone_number, purpose=purpose, is_used=False
        ).update(is_used=True)

        return cls.objects.create(
            phone_number=phone_number,
            purpose=purpose,
            code=cls.generate_code(),
        )

    def verify(self, code: str) -> bool:
        """
        Check the given code. Increments attempts on failure.
        Marks as used on success.
        """
        if not self.is_valid:
            return False

        if self.code != code:
            self.attempts += 1
            self.save(update_fields=["attempts"])
            return False

        self.is_used = True
        self.save(update_fields=["is_used"])
        return True
