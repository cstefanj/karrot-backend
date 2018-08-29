# Generated by Django 2.1 on 2018-08-29 18:22

from django.db import migrations
from django.db.models import Q, F


def set_latest_message(apps, schema_editor):
    Conversation = apps.get_model('conversations', 'Conversation')
    ConversationMessage = apps.get_model('conversations', 'ConversationMessage')

    for c in Conversation.objects.all():
        try:
            c.latest_message = c.messages.filter(Q(thread_id=None) | Q(id=F('thread_id'))).latest('id')
            c.save()
        except ConversationMessage.DoesNotExist:
            c.latest_message = None
            c.save()


class Migration(migrations.Migration):

    dependencies = [
        ('conversations', '0021_conversationmessage_edited_at'),
    ]

    operations = [migrations.RunPython(set_latest_message, migrations.RunPython.noop, elidable=True)]
