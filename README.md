[![Ignite](https://user-images.githubusercontent.com/882381/45938197-49cfb880-bf7c-11e8-91ea-94fffd9d054a.png)](https://github.com/sumukh/ignite)

# Ignite for Flask [![CircleCI](https://circleci.com/gh/Sumukh/Ignite.svg?style=svg&circle-token=21024628f8356bc070f27aede670fc676a8e4446)](https://circleci.com/gh/Sumukh/Ignite)

Ignite is a scaffold for starting new Flask applications. It takes care of the boilerplate code (like User Registration, OAuth, Teams, and Billing), allowing you to focus on building your application. Ignite is built upon best practices for modern Flask applications.

## Features
| Features  |   Status | Details
| ------------- | ------------- | -------- |
| User Authentication  | ✅  | User Login, Signup, Forgot Password, Email Confirmation|
| OAuth Login  | ✅ | Login & Signup with Google, Twitter, Facebook, etc.
| Teams/Groups | ✅  | Multi user teams & groups (with Invite Emails)
| User Export & Deletion Request  | ✅ | Allows users to export their data  (for GDPR compliance)
| API  | ✅  | API (with user tokens) users to access data
| Stripe Product Checkout  | ✅  | One time item purchases with credit cards and receipts (using Stripe)
| Heroku/Docker Deployment  | ✅  | Deployment instructions for some platforms. Works on AWS & Google Cloud
| Send Emails | ✅  | Send email notifications from the application
| Admin Dashboard | ✅  | Admin dashboard to edit data
| Basic Test Suite | ✅  | Starting point for you to build out tests
| VS Code Debugger & Editor | ✅  | Configured to make you productive
| Tested on Windows, OSX, and Ubuntu | ✅  | (Using WSL)
| SaaS Recurring Billing  | ✅ | Requires a purchased license (included with a purchase of Ignite Pro) |
| Commercial Usage  | ❌  | Requires a purchased license (included with a purchase of Ignite Pro)
| Video Content | ❌ | (available in Ignite Pro)

## Setup
Usage of Python 3 is recommended. It can be installed [on Python.org](https://www.python.org/downloads/)
```
# Optional but recommended:
python3 -m venv env; source env/bin/activate

pip install -r requirements.txt
./manage.py server # or `FLASK_APP=manage FLASK_ENV=development flask run`
```
## Running

```
# Development
# If using a virtual env: source env/bin/activate
./manage.py resetdb # to seed data
FLASK_APP=manage FLASK_ENV=development flask run

# Go to localhost:5000 in a browser and click on Login
# Login with the following credentials "user@example.com", "test

# Production documentation in the repository.
```

### Local Secrets

To configure OAuth login and Stripe billing in development, you will need to set some environment variables. See `.env.local.sample` for an example.

```bash
cp .env.local.sample .env.local
# Edit .env.local with your Stripe & Google test keys
source .env.local
flask run
```

You may also want to change some of the constants in `appname.constants`


## License

This is a commercial product. You may purchase a license for commercial use at [Ignite Website](https://ignite.sumukh.me)

Here's a summary:


| Features | Ignite | (License) Ignite Premium | Comments |
| ------------- | ------------- | ---------- | ------- |
| Cost | Free | $199 per site | Currently on sale  |
| Private Non Commercial Use | ✅ | ✅ |
| Commercial Use  | No  |  ✅  |
| Ability to remove "Powered by Ignite" footer | No  |  ✅  |
| Video Tutorials | No  |  ✅  |
| Re-license | No  |  Contact us |
| Support | No  |  No |
| Warranty  | No  |  No | Provided As-is
| Refunds  | N/A  |  30 Day |

You can purchase a license at the [Ignite Website](https://ignite.sumukh.me)

For more detailed license information see LICENSE.md

## Deployment

Ignite is not tied to a specific platform for deployment, but it works well on [Heroku](http://heroku.com) and [Dokku](http://dokku.viewdocs.io/dokku/) with minimal configuration.

It is also designed to work well on other cloud providers such as AWS, Google Cloud, and DigitalOcean.

Documentation is currently provided for installations on Dokku.

## Screenshots


Login Page:
![login](documentation/screenshots/login.png)

GDPR/Legal:
![legal](documentation/screenshots/gdpr.png)

Team Management:
![team](documentation/screenshots/team.png)

Dashboard:
![user dashboard](documentation/screenshots/dashboard.png)

Admin Console:
![admin](https://user-images.githubusercontent.com/882381/33539038-326c31cc-d879-11e7-981a-1834f15cf718.png)

## Credits

Design elements from [tabler](https://github.com/tabler/tabler) & Bootstrap 4.


Built off of [Flask Foundation](https://jackstouffer.github.io/Flask-Foundation/) and the [bootstrapy project](https://github.com/kirang89/bootstrapy)


### Extra Reading

Best practices List:
* [Larger Applications With Flask](http://flask.pocoo.org/docs/patterns/packages/).
* [Creating Websites With Flask](http://maximebf.com/blog/2012/10/building-websites-in-python-with-flask/)
* [Getting Bigger With Flask](http://maximebf.com/blog/2012/11/getting-bigger-with-flask/)
* [Miguel Grinberg's Blog](https://blog.miguelgrinberg.com/category/Python)
