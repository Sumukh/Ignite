def pluralize(number, singular='', plural='s'):
    """ Pluralize filter for Jinja.
    Source: http://stackoverflow.com/a/22336061/411514
    """
    if number == 1:
        return singular
    return plural
