from appname.models import db, Model

class TeamFile(Model):
    id = db.Column(db.Integer(), primary_key=True)
    team_id = db.Column(db.ForeignKey("team.id"), index=True,
                        nullable=False)
    user_id = db.Column(db.ForeignKey("user.id"), index=True,
                        nullable=True)

    file_name = db.Column(db.String())
    description = db.Column(db.String())

    file_object_name = db.Column(db.String())

    activated = db.Column(db.Boolean(), default=False)

    team = db.relationship("Team", backref='files', lazy="joined")
    user = db.relationship("User", backref='team_files')

    GDPR_EXPORT_COLUMNS = {
        "created": "When the invite was created",
        "team_id": "What team was the invite for",
        "creator_id": "Who created the file",
        "file_name": "The name of the file",
        "description": "The description of the file",
    }
