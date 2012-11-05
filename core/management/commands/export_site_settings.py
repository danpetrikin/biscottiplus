from django.core.management.base import BaseCommand, CommandError
from django.core import serializers

from core.models import AppSettings

class Command(BaseCommand):
    args = '<filename ...>'
    help = 'export the site settings (optional args: filename)'

    def handle(self, *args, **options):
        filename = 'settings.xml'
        for name in args:
            filename = name
        
        with open(filename, "w") as out:
            XMLSerializer = serializers.get_serializer("xml")
            xml_serializer = XMLSerializer()
            xml_serializer.serialize(AppSettings.objects.all(), stream=out)
        
        self.stdout.write('Export created at: '+ filename + '\n')