from flask_assets import Bundle

common_css = Bundle(
    'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css',
    'css/vendor/helper.css',
    'css/main.css',
    'css/overrides.css',
    filters='cssmin',
    output='public/css/common-1.css'
)

common_js = Bundle(
    'https://code.jquery.com/jquery-3.2.1.slim.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js',
    'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js',
    Bundle(
        'js/main.js',
        filters='jsmin'
    ),
    output='public/js/common-2.js'
)

store_css = Bundle(
    'css/store.css',
    filters='cssmin',
    output='public/css/store.css'
)

landing_css = Bundle(
    'css/landing.css',
    filters='cssmin',
    output='public/css/landing.css'
)

tabler_css = Bundle(
    'https://rawcdn.githack.com/Sumukh/Ignite/70bf953851a356e785528b56ca105042074a3d5a/appname/static/tabler/css/dashboard.css',
    'css/overrides.css',
    filters='cssmin',
    output='public/css/tabler.css'
)

tabler_js = Bundle(
    'tabler/js/vendors/jquery-3.2.1.min.js',
    'tabler/js/vendors/bootstrap.bundle.min.js',
    'tabler/js/vendors/circle-progress.min.js',
    'tabler/js/vendors/selectize.min.js',
    'tabler/js/vendors/jquery.tablesorter.min.js',
    'tabler/js/core.js',
    output='public/js/tabler.js'
)

tabler_plugins_css = Bundle(
    'tabler/js/plugins/charts-c3/plugin.css',
    output='public/css/tabler-plugins.css'
)

tabler_plugins_js = Bundle(
    'tabler/js/vendors/chart.bundle.min.js',
    'tabler/js/vendors/jquery.sparkline.min.js',
    'tabler/js/vendors/jquery-jvectormap-2.0.3.min.js',
    'tabler/js/vendors/jquery-jvectormap-de-merc.js',
    'tabler/js/vendors/jquery-jvectormap-world-mill.js',
    'tabler/js/plugins/charts-c3/js/d3.v3.min.js',
    'tabler/js/plugins/charts-c3/js/c3.min.js',
    'tabler/js/plugins/input-mask/js/jquery.mask.min.js',
    # Other Plugins as needed.
    output='public/js/tabler-plugins.js'
)
