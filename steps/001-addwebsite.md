<div dir="rtl">

به عنوان اولین مرحله برای ساخت یک اپ جدید با دستورات پیش فرض جنگو و معماری یک اپ جدید ایجاد میکنیم:

<div dir="ltr">

```text
cd core
uv run manage.py startapp website apps/website
```

</div>

حالا وارد کانفیگ پروژه میشیم و در قسمت settings.py اپ جدید رو اضافه میکنیم و سپس در قسمت urls.py هم آدرس اپ جدید رو اضافه میکنیم:

<div dir="ltr">

`core/config/settings.py`

```text
INSTALLED_APPS = [
    .
    .
    .
    "apps.orders",
    "apps.payments",
    "apps.users",
    "apps.website"
    .
    .
    .
]
```

</div>

<div dir="ltr">

`core/config/urls.py`

```text
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.website.urls")),
]
```

</div>

حالا باید وارد اپ وبسایت بشیم و آدرس های لازم برای این اپ رو مشخص کنیم برای این کار باید چنین ساختاری برای استاندارد بودن این اپ داشته باشیم :

<div dir="ltr">

`core/apps/website/urls.py`

```text
from django.urls import path

from . import views

app_name = "website"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("contact/", views.ContactView.as_view(), name="contact"),
]

```

</div>

حالا برای کار کردن این قسمت نیاز داریم یک کلاس برای هر صفحه در قسمت views داشته باشیم و یک فایل html برای رندر شدن توسط موتور جنگو:

<div dir="ltr">

`core/apps/website/views.py`

```text
from django.views.generic import TemplateView

from .models import *


class IndexView(TemplateView):
    template_name = "website/index.html"


class ContactView(TemplateView):
    template_name = "website/contact.html"


class AboutView(TemplateView):
    template_name = "website/about.html"


```

</div>

در آخرین مرحله هم باید در فایل apps.py اپ وبسایت نام و مشخصات اپ را مشخص کنیم تا هسته بتواند این اپ را شناسایی کند:

<div dir="ltr">

`core/apps/website/apps.py`

```text
from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.website"



```

</div>

</div>
