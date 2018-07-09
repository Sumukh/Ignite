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
    'tabler/css/tabler.css',
    'tabler/css/dashboard.css',
    filters='cssmin',
    output='public/css/tabler.css'
)

tabler_js = Bundle(
    Bundle(
        'tabler/js/vendors/jquery-3.2.1.min.js',
        'tabler/js/vendors/bootstrap.bundle.min.js',
        'tabler/js/vendors/circle-progress.min.js',
        'tabler/js/vendors/selectize.min.js',
        'tabler/js/vendors/jquery.tablesorter.min.js',
    ),
    'tabler/js/core.js',
    output='public/js/tabler.js'
)

tabler_plugins_js = Bundle(
    'tabler/js/vendors/chart.bundle.min.js',
    'tabler/js/vendors/jquery.sparkline.min.js',
    'tabler/js/vendors/jquery.jvector-map-2.0.3.min.js',
    'tabler/js/vendors/jquery.jvector-map-de-merc.min.js',
    'tabler/js/vendors/jquery.jvector-map-world-mill.min.js',
    # Other Plugins as needed.
    output='public/js/tabler-plugins.js'
)
