import logging
import json
from collections import defaultdict

from flask_mail import Attachment

from appname.mailers.notification import NotificationMailer

logger = logging.getLogger(__name__)

class GDPRExport:
    def __init__(self, user, requesting_user):
        self.user = user
        self._requesting_user = user

        if user != requesting_user and not requesting_user.is_admin:
            raise Exception('Cannot export report; Not enough permission')

    def send_pii_export(self):
        json_str = self.export_user_pii_json()
        attachment = Attachment(filename="user_export.json", content_type="application/json", data=json_str)
        mailer = NotificationMailer(self._requesting_user.email, "appname User Data Export",
                                    "Your requested export is attached below", attachments=[attachment])
        mailer.send()

    def export_user_pii_json(self):
        related_models_accessors = ['active_teams', 'memberships']
        models_to_export = [getattr(self.user, accessor) for accessor in related_models_accessors]

        export = defaultdict(list)

        for sublist in models_to_export:
            for item in sublist:
                export_data = item.gdpr_export_pii_data()
                if export_data:
                    # This will produce odd results if two model classes have the same name
                    export[str(item.__class__.__name__)].append(export_data)
        for provider in self.user.oauth:
            export['OAuth'].append(self.user.oauth[provider].gdpr_export_pii_data())

        export['User'] = self.user.gdpr_export_pii_data()

        return json.dumps(export, indent=4)
