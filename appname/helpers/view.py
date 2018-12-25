# View Helpers that we want to be available globally in Jinja templates
# as `view_helpers.method`

def format_money(amount, currency):
    return "{0} {1}".format(amount, currency)
