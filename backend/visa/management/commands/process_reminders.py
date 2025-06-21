from django.core.management.base import BaseCommand
from django.utils import timezone
from services.schedule_service import default_schedule_service


class Command(BaseCommand):
    help = 'Process due reminders and send notification emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without actually sending emails',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of reminders to process (default: 100)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting reminder processing at {timezone.now()}')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No emails will be sent')
            )
            
            # Get due reminders without processing them
            due_reminders = default_schedule_service.get_due_reminders(limit=limit)
            
            if not due_reminders:
                self.stdout.write('No due reminders found.')
                return
            
            self.stdout.write(f'Found {len(due_reminders)} due reminders:')
            for reminder in due_reminders:
                self.stdout.write(
                    f'  - {reminder["title"]} ({reminder["reminder_type"]}) '
                    f'for {reminder["user_email"]} - Due: {reminder["reminder_date"]}'
                )
        else:
            # Actually process the reminders
            result = default_schedule_service.process_due_reminders()
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully processed {result["processed"]} reminders: '
                        f'{result["sent"]} sent, {result["failed"]} failed'
                    )
                )
                
                if result['failed'] > 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f'{result["failed"]} reminders failed to send. Check logs for details.'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error processing reminders: {result.get("error", "Unknown error")}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Reminder processing completed at {timezone.now()}')
        ) 