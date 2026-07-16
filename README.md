# ThirdEyeAnalytics

This is my final project for ITC4214 Internet Programming at Deree.

ThirdEye is a fictional football analytics company. The website sells services
such as player tracking, heatmaps, tactical reports, scouting reports and
automatic highlight detection. It works like a small online shop, but checkout
is only a simulation and no real payment is made.

## What the website can do

- Anyone can view the home page and browse the service catalogue.
- Services can be searched by name or analysis type.
- The catalogue can be filtered by category, price, skill level, video type,
  delivery time and output format.
- Users can register, log in and edit their profile.
- Logged-in users can save services to a wishlist and rate them with stars.
- Users can add services to their cart and complete a simulated checkout.
- The user dashboard shows recent views, saved services, ratings, orders and
  recommendations.
- Administrators can add, edit and delete services, categories and
  sub-categories from the management pages.
- Head Administrators can also change user roles and access Django Admin.

The recommendations are rule based. They use the user's latest search, viewed
service categories and wishlist. There is no machine learning or external AI
service used by the website.

## Technologies

- Python
- Django
- SQLite
- HTML and CSS
- JavaScript and jQuery
- Pillow for checking uploaded images

I kept the project as a normal Django application. I did not use a separate API,
front-end framework, payment service or cloud database because they are not
needed for this project.

## User roles

There are four types of visitor:

- Viewer: can browse and search without an account.
- User: can use the dashboard, wishlist, ratings, cart and checkout.
- Administrator: can also use the website management pages.
- Head Administrator: can change roles and use Django Admin.

Django's `is_staff` and `is_superuser` fields are used for the real permission
checks. The role saved in the profile is used to show the role clearly on the
website.

## Security used in the project

- Django ORM is used instead of writing SQL queries by hand.
- Django templates escape user content before showing it in HTML.
- Every form that changes data uses CSRF protection.
- Django hashes passwords before saving them.
- Login checks protect user pages and staff checks protect management pages.
- Cart items and orders are always looked up through the logged-in user.
- Uploaded images have file size, file type and image dimension limits.
- Categories and sub-categories used by a service cannot be deleted by mistake.
- Services saved in an order cannot be deleted, so old order details stay valid.
- The Content Security Policy only allows the scripts and files used by this
  website.

## Running the project locally

Open PowerShell in the project folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_catalogue
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Then open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

If the virtual environment and database are already set up, I only need:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

## Main pages

- Home: `http://127.0.0.1:8000/`
- Services: `http://127.0.0.1:8000/services/`
- Register: `http://127.0.0.1:8000/accounts/register/`
- Login: `http://127.0.0.1:8000/accounts/login/`
- User dashboard: `http://127.0.0.1:8000/dashboard/`
- Management dashboard: `http://127.0.0.1:8000/management/`
- Django Admin: `http://127.0.0.1:8000/django-admin/`

## Demo accounts

The local database has these accounts for testing:

```text
Head Administrator: headadmin / HeadAdmin123!
Administrator: administrator / Admin12345!
User: user / User12345!
```

The database file is not uploaded to GitHub. On a new setup, a superuser can be
created with:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

## Testing

I use Django's checks and automated tests before running the website:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

The tests cover registration, permissions, catalogue management, protected
deletions, filters, recommendations, ratings, the cart, checkout, form
validation and the main security checks.

## Project structure

- `accounts` handles users, profiles, dashboards and staff management.
- `catalogue` handles categories, services, filters and recommendations.
- `interactions` handles ratings, wishlists, recent views and search history.
- `cart` handles cart items, billing details and simulated orders.
- `core` handles shared pages such as the home page.
- `config` contains the main Django settings and URL setup.
- `templates` contains the page structure.
- `static` contains the CSS, JavaScript and images.

The code has comments beside the parts that need explanation. Generated Django
migrations and the minified jQuery file are left unchanged because they are not
handwritten project code.

## Repository

https://github.com/harouklas/ThirdEyeAnalytics

## Links to add before submission

- Deployment: not added yet
- Demonstration video: not added yet
