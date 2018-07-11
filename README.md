# Ignite for Flask [![CircleCI](https://circleci.com/gh/Sumukh/Ignite.svg?style=svg&circle-token=21024628f8356bc070f27aede670fc676a8e4446)](https://circleci.com/gh/Sumukh/Ignite)

Ignite is a scaffold for starting new Flask applications. It takes care of the boilerplate code (like User Registration), allowing you to focus on building your application. Ignite is built upon best practices for modern Flask applications.

## Features
| Features  |   Status |
| ------------- | -------------
| Authentication  | ✅  |
| Teams/Groups | ✅  |
| Email Confirmation/Password Resets  | ✅  |
| OAuth Login (Login via Twitter etc...)  | ✅ |
| API  | ✅  |
| Stripe Product Checkout  | ✅  |
| Heroku/Docker Deployment  | ✅  |
| DB Migrations | ✅  |
| Send Emails | ✅  |
| Admin Dashboard | ✅  |
| Basic Test Suite | ✅  |
| Customizable | ✅  |
| Commercial Usage  | ❌  (available in Ignite Premium)  |


## Ignite Premium

A license to premium allows you to use all the features in Ignite Basic

| Features | Ignite Basic | Ignite Premium |
| ------------- | ------------- | ---------- |
| License for Commercial Use  | No  |  ✅  |
| Remove "Powered by Ignite" badge  | Must be included  |  ✅  |
| Video Tutorials  | No |  🔜 Coming Soon  |
| Recurring Subscription Support (via Stripe)  | No  | Contact Us (Starting from $999 extra) |

You can purchase a license on [ignite.sumukh.me](https://ignite.server.sumukh.me/store)

## Setup
Usage of Python 3 is recommended. It can be installed [on Python.org](https://www.python.org/downloads/)
```
# Optional but recommended: python3 -m venv env; source env/bin/activate

pip install -r requirements.txt
./manage.py server
```

## Running

```
# Development
# If using a virtual env: source env/bin/activate
./manage.py server

# Production instructions below
```

## License

This is a commercial product. You may purchase a license for commercial use at [ignite.sumukh.me](ignite.sumukh.me)

Here's a summary:


| Features | Ignite | (License) Ignite Premium | Comments |
| ------------- | ------------- | ---------- | ------- |
| Cost | Free | $100 per site | Currently on sale  |
| Private Non Commercial Use | ✅ | ✅ |
| Commercial Use  | No  |  ✅  |
| Ability to remove "Powered by Ignite" footer | No  |  ✅  |
| Re-license | No  |  Contact us |
| Warranty  | No  |  No | Provided As-is
| Refunds  | N/A  |  30 Day |

You can purchase a license at the [Ignite demo store](https://ignite.server.sumukh.me/store)


For more detailed license information see LICENSE.md

## Deployment

Ignite is not tied to a specific platform for deployment, but it works well on [Heroku](http://heroku.com) and [Dokku](http://dokku.viewdocs.io/dokku/) with minimal configuration.

It is also designed to work well on other cloud providers such as AWS, Google Cloud, and DigitalOcean.

Documentation is currently provided for installations on Dokku. Documentation for other providers can be provided with a purchase of a license of Ignite Premium.

## Screenshots

Home Page:
![homepage](https://user-images.githubusercontent.com/882381/33538945-ca50c3f0-d878-11e7-9b6e-8aba804dd227.png)

Login Page:
![loginpage](https://user-images.githubusercontent.com/882381/33538980-f6f522de-d878-11e7-8efc-93c801cbcf16.png)

Settings Page:
![user dashboard](https://user-images.githubusercontent.com/882381/33539079-631fc2e8-d879-11e7-802e-454bf3104ae2.png)

Admin Console:
![admin](https://user-images.githubusercontent.com/882381/33539038-326c31cc-d879-11e7-981a-1834f15cf718.png)


## Credits

Built off of [Flask Foundation](https://jackstouffer.github.io/Flask-Foundation/) and the [bootstrapy project](https://github.com/kirang89/bootstrapy)


### Extra Reading

Best practices List:
* [Larger Applications With Flask](http://flask.pocoo.org/docs/patterns/packages/).
* [Creating Websites With Flask](http://maximebf.com/blog/2012/10/building-websites-in-python-with-flask/)
* [Getting Bigger With Flask](http://maximebf.com/blog/2012/11/getting-bigger-with-flask/)
* [Miguel Grinberg's Blog](https://blog.miguelgrinberg.com/category/Python)

