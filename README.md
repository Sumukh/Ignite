[![Ignite](https://user-images.githubusercontent.com/882381/45938197-49cfb880-bf7c-11e8-91ea-94fffd9d054a.png)](https://github.com/sumukh/ignite)

# Ignite for Flask [![CircleCI](https://circleci.com/gh/Sumukh/Ignite.svg?style=svg&circle-token=21024628f8356bc070f27aede670fc676a8e4446)](https://circleci.com/gh/Sumukh/Ignite)

Ignite is a scaffold for starting new Flask applications. It takes care of the boilerplate code (like User Registration), allowing you to focus on building your application. Ignite is built upon best practices for modern Flask applications.

## Features
| Features  |   Status | Details
| ------------- | ------------- | -------- |
| User Authentication  | ✅  | User Login, Signup, Forgot Password, Email Confirmation|
| OAuth Login  | ✅ | Login & Signup with Google, Twitter, Facebook, etc.
| Teams/Groups | ✅  | Multi user teams & groups
| User Export & Deletion  | ✅ | Allows users to export or delete their data  (for GDPR compliance)
| API  | ✅  | API for users to access data
| Stripe Product Checkout  | ✅  | One time item purchases with credit cards and receipts (using Stripe)
| Heroku/Docker Deployment  | ✅  | Deployment instructions for some platforms. Works on AWS & Google Cloud
| Send Emails | ✅  | Send email notifications from the application
| Admin Dashboard | ✅  | Admin dashboard to edit data
| Basic Test Suite | ✅  | Starting point for you to build out tests
| Commercial Usage  | ❌  | Requires a purchased license (included with a purchase of Ignite Pro)
| SaaS Recurring billing with Stripe | ❌ | (available in Ignite Pro)
| Landing Page Design Usage | ❌ | (available in Ignite Pro)

## Setup
Usage of Python 3 is recommended. It can be installed [on Python.org](https://www.python.org/downloads/)
```
# Optional but recommended:
python3 -m venv env; source env/bin/activate

pip install -r requirements.txt
./manage.py server
```
## Running

```
# Development
# If using a virtual env: source env/bin/activate
./manage.py resetdb # to seed data
./manage.py server

# Login with the following credentials "user@example.com", "test

# Production documentation in the repository.
```


## Ignite Premium

A license to premium allows you to use all the features in Ignite Basic in addition to:

| Features | Ignite Basic | Ignite Pro |
| ------------- | ------------- | ---------- |
| License for Commercial Use  | No  |  ✅  |
| Remove "Powered by Ignite" badge  | Must be included  |  ✅  |
| Video Tutorials  | No |  🔜 Coming Soon  |
| Recurring Subscription Support (via Stripe)  | No  | Contact Us (Starting at $799) |

You can purchase a license by emailing the author.


## License

This is a commercial product. You may purchase a license for commercial use at [Ignite Website](https://ignite.sumukh.me)

Here's a summary:


| Features | Ignite | (License) Ignite Premium | Comments |
| ------------- | ------------- | ---------- | ------- |
| Cost | Free | $199 per site | Currently on sale  |
| Private Non Commercial Use | ✅ | ✅ |
| Commercial Use  | No  |  ✅  |
| Ability to remove "Powered by Ignite" footer | No  |  ✅  |
| Re-license | No  |  Contact us |
| Warranty  | No  |  No | Provided As-is
| Refunds  | N/A  |  30 Day |

You can purchase a license at the [Ignite Website](https://ignite.sumukh.me)

For more detailed license information see LICENSE.md

## Deployment

Ignite is not tied to a specific platform for deployment, but it works well on [Heroku](http://heroku.com) and [Dokku](http://dokku.viewdocs.io/dokku/) with minimal configuration.

It is also designed to work well on other cloud providers such as AWS, Google Cloud, and DigitalOcean.

Documentation is currently provided for installations on Dokku. Documentation for other providers can be provided with a purchase of a license of Ignite Premium.

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
