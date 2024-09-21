from flask_assets import Bundle

common_css = Bundle(
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
    'css/vendor/helper.css',
    'css/main.css',
    'css/overrides.css',
    filters='cssmin',
    output='public/css/common-1.css'
)

common_js = Bundle(
    'https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js',
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
    'https://cdn.jsdelivr.net/npm/@tabler/core@latest/dist/css/tabler.min.css',
    'https://cdn.jsdelivr.net/npm/@tabler/core@1.0.0-beta21/dist/css/tabler-vendors.min.css',
    'css/overrides.css',
    filters='cssmin',
    output='public/css/tabler.css'
)

tabler_js = Bundle(
    'https://cdn.jsdelivr.net/npm/@tabler/core@1.0.0-beta21/dist/js/tabler.min.js',
    output='public/js/tabler.js'
)

tabler_plugins_css = Bundle(
    'tabler/js/plugins/charts-c3/plugin.css',
    output='public/css/tabler-plugins.css'
)

tabler_plugins_js = Bundle(
    'https://cdn.jsdelivr.net/npm/apexcharts',
    'https://cdn.jsdelivr.net/npm/choices.js@9.0.1/public/assets/scripts/choices.min.js',
    'https://cdn.jsdelivr.net/npm/litepicker/dist/litepicker.js',
    'https://cdn.jsdelivr.net/npm/tom-select@2.3.1/dist/js/tom-select.complete.min.js',
    # Other Plugins as needed.
    output='public/js/tabler-plugins.js'
)
