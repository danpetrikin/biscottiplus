from django.core.management.base import BaseCommand, CommandError
from django.core import serializers

from core.models import AppSettings

class Command(BaseCommand):
    args = '<filename ...>'
    help = 'import the site settings (optional args: filename)'

    def handle(self, *args, **options):
        filename = 'settings.xml'
        for name in args:
            filename = name
        
        f = open(filename)
        
        for obj in serializers.deserialize("xml", f.read()):
            obj.save()
        
        self.stdout.write('Import successful from: '+ filename + '\n')