from flask_assets import Bundle

common_css = Bundle(
    'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css',
    'css/vendor/helper.css',
    'css/main.css',
    filters='cssmin',
    output='public/css/common.css'
)

common_js = Bundle(
    'https://code.jquery.com/jquery-3.2.1.slim.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.3/umd/popper.min.js',
    'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/js/bootstrap.min.js',
    Bundle(
        'js/main.js',
        filters='jsmin'
    ),
    output='public/js/common.js'
)

store_css = Bundle(
    'css/store.css',
    filters='cssmin',
    output='public/css/store.css'
)

tabler_css = Bundle(
    'css/vendor/tabler/tabler.css',
    'css/vendor/tabler/dashboard.css',
    filters='cssmin',
    output='public/css/tabler.css'
)

# We don't use Flask Assets for Tabler Js

tabler_js = Bundle(
    'public/tabler/js/require.min.js',
    output='public/js/tabler.js'
)
