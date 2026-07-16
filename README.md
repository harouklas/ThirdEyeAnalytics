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

## Download and run the website from GitHub

If someone only wants to see the finished website, there is nothing to
download. The deployed website can be opened here:
[https://charischaliotis.pythonanywhere.com/](https://charischaliotis.pythonanywhere.com/).

The steps below explain how to download the code from GitHub and run a separate
local copy on a Windows computer. Python 3.12 or newer and Git must be installed
first. Visual Studio Code is optional.

### 1. Check that Python and Git are installed

Open PowerShell and run:

```powershell
py --version
git --version
```

- `py --version` shows the installed Python version. It must be 3.12 or newer.
- `git --version` checks that Git is installed and available in PowerShell.

If either command is not recognised, install that program before continuing.

### 2. Download the project with Git

Open PowerShell inside the folder where the project should be saved, then run:

```powershell
git clone https://github.com/harouklas/ThirdEyeAnalytics.git
cd ThirdEyeAnalytics
```

- `git clone` downloads the complete project and its Git history from GitHub.
- `cd ThirdEyeAnalytics` moves PowerShell inside the downloaded project folder.

The correct folder is the one that contains `manage.py`, `README.md`,
`requirements.txt` and the Django application folders. This is also the folder
that should be opened in Visual Studio Code. If the `code` command is installed,
it can be opened from PowerShell with:

```powershell
code .
```

`code .` opens the current folder in Visual Studio Code. The website can still
be set up without using this command.

#### Downloading without Git

The other option is to open the GitHub repository, press **Code**, press
**Download ZIP**, and extract the ZIP file. Open PowerShell inside the extracted
`ThirdEyeAnalytics-main` folder and continue from step 3. A ZIP download does
not include the Git history, so `git pull` cannot be used to update it later.

### 3. Create the virtual environment

Run this from the folder that contains `manage.py`:

```powershell
py -m venv .venv
```

This creates a private Python environment inside `.venv`. It keeps this
project's packages separate from other Python projects. The `.venv` folder is
ignored by Git and is not uploaded to GitHub.

The commands below use the Python file inside `.venv` directly. This means the
environment does not need to be activated separately.

### 4. Install the required packages

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

This reads `requirements.txt` and installs the exact Django and Pillow versions
used by the project. Django runs the website and Pillow checks uploaded images.

### 5. Create the local database tables

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

`migrate` creates the local SQLite database and all tables required by the
project. The new database is saved as `db.sqlite3`. It is not downloaded from
GitHub and it is not uploaded back to GitHub.

### 6. Add the example catalogue

```powershell
.\.venv\Scripts\python.exe manage.py seed_catalogue
```

This adds the example categories, sub-categories and services used by the
website. It can be run again without creating duplicate catalogue records.

### 7. Add the three demo accounts

```powershell
.\.venv\Scripts\python.exe manage.py seed_demo_users
```

This creates `headadmin`, `administrator` and `user` with the passwords listed
in the Demo accounts section below. It also gives each account the correct role
and permission settings. Running it again resets the same three accounts instead
of creating duplicates.

### 8. Check the project

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

- `check` looks for problems in the Django settings, models and URL setup.
- `test` runs the automated tests for the main website actions and permissions.

The website can still be started after `check` passes. The full test command can
take a little longer because it creates a temporary test database.

### 9. Start the local website

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

`runserver` starts Django's local development server on port 8000. Keep this
PowerShell window open while using the website, then open
[http://127.0.0.1:8000/](http://127.0.0.1:8000/) in a browser.

Press `Ctrl + C` in PowerShell when the local server should stop.

### 10. Open the website again later

After the first setup, there is no need to reinstall everything each time.
Open PowerShell in the `ThirdEyeAnalytics` folder and run:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

The same local database, catalogue and accounts will still be there unless
`db.sqlite3` or the whole project folder was deleted.

### Updating a copy downloaded with Git

To download newer changes from the GitHub repository, stop the server and run:

```powershell
git pull
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
```

- `git pull` downloads and applies the newest committed code.
- The `pip install` command installs any package changes in `requirements.txt`.
- `migrate` applies any new database changes without deleting existing data.

## Main pages

- Home: `http://127.0.0.1:8000/`
- Services: `http://127.0.0.1:8000/services/`
- Register: `http://127.0.0.1:8000/accounts/register/`
- Login: `http://127.0.0.1:8000/accounts/login/`
- User dashboard: `http://127.0.0.1:8000/dashboard/`
- Management dashboard: `http://127.0.0.1:8000/management/`
- Django Admin: `http://127.0.0.1:8000/django-admin/`

## Demo accounts

The database is not uploaded to GitHub. After downloading the project, the
`seed_demo_users` command creates these three local accounts for testing:

```text
Head Administrator: headadmin / HeadAdmin123!
Administrator: administrator / Admin12345!
User: user / User12345!
```

The command can be run again without creating duplicates. It resets these three
accounts so their passwords and permissions still match this section. The local
command only runs while `DJANGO_DEBUG` is `True`.

The deployed coursework website also has these same three accounts. Their
passwords are public because they are only demonstration accounts, so no real or
private information should be saved in them.

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

## Deployment

https://charischaliotis.pythonanywhere.com/

## Demonstration video

Not added yet.
