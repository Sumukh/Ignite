# Utility methods to grab info from the current session
from flask import session, redirect, flash, url_for
from flask_login import current_user

def current_membership():
    session_id = session.get('current_team_membership_id')
    memberships = current_user.active_memberships
    if not session_id:
        return memberships[0]
    elif session_id and session_id in [m.id for m in memberships]:
        return [m for m in memberships if m.id == session_id][0]
    else:
        # TODO: Should just raise an exception here.
        flash('You currently do not have accesss to appname', 'warning')
        return redirect(url_for("main.home"))
