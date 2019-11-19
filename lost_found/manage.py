# -*- coding: utf-8 -*-
from flask.cli import FlaskGroup
from project import create_app, db
from project.models.models import Users, Items

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command()
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command()
def seed_db():
    """Seeds the database."""
    db.session.add()
    db.session.add()
    db.session.commit()


if __name__ == '__main__':
    cli()
