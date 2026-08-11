<div dir="rtl">

# معماری دیتابیس

این معماری دیتابیس با هدف پوشش کامل نیازهای یک فروشگاه اینترنتی در مقیاس کوچک تا متوسط
طراحی شده است و میتواند در این سطح تمامی نیاز های یک فروشگاه را تامین کند.

---

# نمای کلی دیتابیس

```mermaid
erDiagram

    User ||--o{ Product : lists
    User ||--o{ Order : places
    User ||--o{ Comment : writes
    User ||--o{ Address : has
    User ||--o{ Cart : owns

    Category ||--o{ Product : categorizes

    Product ||--o{ Order_Item : included_in
    Product ||--o{ Cart_Item : included_in
    Product ||--o{ Comment : receives

    Order ||--o{ Order_Item : contains
    Order ||--o{ Payment : has
    Order }o--|| Address : ships_to

    Discount ||--o{ Discount_Order : applied_to
    Order ||--o{ Discount_Order : uses

    Cart ||--o{ Cart_Item : contains
```

---

# ۱. مدیریت کاربر و دسترسی

```mermaid
erDiagram

    User {
        int id PK
        varchar first_name
        varchar last_name
        varchar mobile
        varchar email
        varchar password
        boolean is_staff
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

```

### توضیح تصمیم

- `is_staff` مشخص می‌کند کاربر به پنل مدیریت دسترسی دارد یا نه (معادل توکار Django).
- `is_superuser` هم به‌صورت توکار در Django موجود است و نیازی به تعریف دستی ندارد
  (در دیاگرام برای اختصار نیامده).

---

# ۲. مدیریت محصول

```mermaid
erDiagram

    Category {
        int id PK
        varchar title
        varchar slug
        int parent_id FK
        timestamp created_at
        timestamp updated_at
    }

    Product {
        int id PK
        int category_id FK
        int user_id FK
        varchar title
        varchar slug
        text description
        decimal price
        decimal compare_at_price
        int stock
        varchar status
        timestamp created_at
        timestamp updated_at
    }

    Product_Image {
        int id PK
        int product_id FK
        varchar path
        boolean is_main
        timestamp created_at
    }

    Feature {
        int id PK
        varchar title
        timestamp created_at
    }

    Product_Feature {
        int product_id FK
        int feature_id FK
        varchar value
    }

    Category ||--o{ Category : parent_of
    Category ||--o{ Product : contains

    Product ||--o{ Product_Image : has
    Product ||--o{ Product_Feature : has

    Feature ||--o{ Product_Feature : defines
```

### وضعیت محصول

<div dir="ltr">

```text
draft         = پیش‌نویس، هنوز منتشر نشده
active        = فعال و قابل خرید
out_of_stock  = موجودی تمام شده (stock = 0)
archived      = بایگانی‌شده / دیگر فروخته نمی‌شود
```

</div>

---

# ۳. سبد خرید (Cart)

```mermaid
erDiagram

    User {
        int id PK
    }

    Product {
        int id PK
    }

    Cart {
        int id PK
        int user_id FK
        timestamp created_at
        timestamp updated_at
    }

    Cart_Item {
        int id PK
        int cart_id FK
        int product_id FK
        int count
        timestamp created_at
        timestamp updated_at
    }

    User ||--o{ Cart : owns
    Cart ||--o{ Cart_Item : contains
    Product ||--o{ Cart_Item : referenced_by
```

---

# ۴. مدیریت سفارش

```mermaid
erDiagram

    User {
        int id PK
    }

    Address {
        int id PK
        int user_id FK
        varchar province
        varchar city
        varchar postal_code
        varchar address_line
        varchar receiver_name
        varchar receiver_mobile
        timestamp created_at
        timestamp updated_at
    }

    Product {
        int id PK
    }

    Order {
        int id PK
        int user_id FK
        int address_id FK
        decimal amount
        decimal final_amount
        varchar status
        timestamp created_at
        timestamp updated_at
    }

    Order_Item {
        int id PK
        int order_id FK
        int product_id FK
        decimal price
        int count
        timestamp created_at
    }

    Payment {
        int id PK
        int order_id FK
        varchar gateway
        varchar authority
        varchar trace_number
        decimal amount
        varchar status
        timestamp paid_at
        timestamp created_at
    }

    User ||--o{ Address : has
    User ||--o{ Order : places
    Address ||--o{ Order : used_in

    Order ||--o{ Order_Item : contains
    Order ||--o{ Payment : has
    Product ||--o{ Order_Item : ordered_as
```

### وضعیت سفارش

<div dir="ltr">

```text
pending      = در انتظار پرداخت
paid         = پرداخت‌شده
processing   = در حال آماده‌سازی
shipped      = ارسال‌شده
delivered    = تحویل داده‌شده
cancelled    = لغوشده
refunded     = مبلغ بازگردانده‌شده
```

</div>

### وضعیت پرداخت

<div dir="ltr">

```text
pending  = در انتظار تایید درگاه
success  = موفق
failed   = ناموفق
```

</div>

---

# ۵. مدیریت تخفیف

```mermaid
erDiagram

    Order {
        int id PK
    }

    User {
        int id PK
    }

    Discount {
        int id PK
        varchar code
        varchar type
        decimal amount
        timestamp expires_at
        int max_use
        int used_count
        varchar description
        timestamp created_at
    }

    Discount_Order {
        int order_id FK
        int discount_id FK
        int user_id FK
        decimal discount_amount
        timestamp created_at
    }

    Order ||--o{ Discount_Order : uses
    Discount ||--o{ Discount_Order : applied_to
    User ||--o{ Discount_Order : redeemed_by
```

---

# ۶. نظرات و امتیازدهی

```mermaid
erDiagram

    User {
        int id PK
    }

    Product {
        int id PK
    }

    Comment {
        int id PK
        int user_id FK
        int product_id FK
        int parent_id FK
        varchar content
        int rating
        boolean is_approved
        timestamp created_at
        timestamp updated_at
    }

    User ||--o{ Comment : writes
    Product ||--o{ Comment : receives
    Comment ||--o{ Comment : replies_to
```

---

# ۷. فهرست کامل موجودیت‌ها

| حوزه           | موجودیت‌ها                                                 |
| -------------- | ---------------------------------------------------------- |
| کاربر و دسترسی | super_user                                                 |
| آدرس           | Address                                                    |
| محصول          | Category, Product, Product_Image, Feature, Product_Feature |
| سبد خرید       | Cart, Cart_Item                                            |
| سفارش          | Order, Order_Item, Payment                                 |
| تخفیف          | Discount, Discount_Order                                   |
| نظرات          | Comment                                                    |

---

# ۸. تصمیمات مهم طراحی

## کلید خارجی و یکپارچگی ارجاعی

تمام روابط با Foreign Key پیاده‌سازی می‌شوند.

## قیدهای یکتایی مهم (Unique Constraints)

این‌ها نکاتی هستند که در نسخه‌ی قبلی به‌صراحت ذکر نشده بودند ولی برای صحت داده حیاتی‌اند:

<div dir="ltr">

```text
User.mobile          → باید یکتا باشد
User.email           → باید یکتا باشد
Product.slug         → باید یکتا باشد
Category.slug        → باید یکتا باشد
Discount.code        → باید یکتا باشد
(Discount_Order.discount_id, Discount_Order.user_id) → باید یکتا باشد
```

</div>

## تراکنش‌ها (Transactions)

عملیات ثبت سفارش باید اتمیک (Atomic) باشد:

```text
ایجاد سفارش → ایجاد اقلام سفارش → کاهش موجودی → Commit
(در صورت خطا در هر مرحله → Rollback کامل)
```

## هم‌زمانی موجودی انبار

<div dir="ltr">

```sql
UPDATE Product
SET stock = stock - 1
WHERE id = $1
AND stock > 0;
```

</div>

---

# ۹. PostgreSQL

PostgreSQL دیتابیس اصلی و Redis برای کش/Session/Rate-limiting استفاده می‌شود.

---

</div>
