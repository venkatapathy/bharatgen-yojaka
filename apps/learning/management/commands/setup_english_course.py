from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.learning.models import LearningPath, Module, Content

class Command(BaseCommand):
    help = 'Setup English Comprehension Course for Grade 8'

    def handle(self, *args, **kwargs):
        self.stdout.write('Setting up English Comprehension Course...')
        
        # Get or create admin user for attribution
        admin_user, _ = User.objects.get_or_create(username='admin')
        
        # 1. Create Learning Path
        path, created = LearningPath.objects.get_or_create(
            slug='english-comprehension-grade-8',
            defaults={
                'title': 'English Comprehension - Grade 8',
                'description': 'A comprehensive course designed to improve reading comprehension skills for 8th-grade students, focusing on poetry and prose analysis.',
                'difficulty_level': 'intermediate',
                'estimated_hours': 10,
                'is_published': True,
                'created_by': admin_user,
                'tags': ['english', 'comprehension', 'grade-8', 'literature']
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created learning path: {path.title}'))
        else:
            self.stdout.write(f'Learning path already exists: {path.title}')
            
        # 2. Create Modules
        modules_data = [
            {
                'title': 'Unit 1: Poetry Analysis',
                'description': 'Learn to analyze poems, understand imagery, and interpret themes.',
                'order': 1,
                'estimated_minutes': 120
            },
            {
                'title': 'Unit 2: Prose Comprehension',
                'description': 'Develop skills to understand narrative structures and character development in prose.',
                'order': 2,
                'estimated_minutes': 120
            }
        ]
        
        modules = {}
        for m_data in modules_data:
            module, _ = Module.objects.get_or_create(
                learning_path=path,
                title=m_data['title'],
                defaults={
                    'description': m_data['description'],
                    'order': m_data['order'],
                    'estimated_minutes': m_data['estimated_minutes']
                }
            )
            modules[m_data['title']] = module
            self.stdout.write(f"Ensured module: {module.title}")
            
        # 3. Create Content
        # Unit 1: Poetry
        poetry_content_data = [
            {
                'title': 'The Road Not Taken - Analysis',
                'content_type': 'text', # Using 'text' type but we'll treat it as a special practice in UI if needed, or maybe 'exercise'
                'order': 1,
                'text_content': """Two roads diverged in a yellow wood,
And sorry I could not travel both
And be one traveler, long I stood
And looked down one as far as I could
To where it bent in the undergrowth;

Then took the other, as just as fair,
And having perhaps the better claim,
Because it was grassy and wanted wear;
Though as for that the passing there
Had worn them really about the same,

And both that morning equally lay
In leaves no step had trodden black.
Oh, I kept the first for another day!
Yet knowing how way leads on to way,
I doubted if I should ever come back.

I shall be telling this with a sigh
Somewhere ages and ages hence:
Two roads diverged in a wood, and I—
I took the one less traveled by,
And that has made all the difference.""",
                'questions': {
                    'type': 'descriptive',
                    'items': [
                        {
                            'id': 1,
                            'question': "What does the 'yellow wood' symbolize in the poem?",
                            'reference_answer': "The 'yellow wood' likely symbolizes autumn, representing a time of change, transition, and maturity. It sets the mood of the poem as somewhat melancholic and reflective."
                        },
                        {
                            'id': 2,
                            'question': "Explain the significance of the phrase 'I took the one less traveled by'.",
                            'reference_answer': "This phrase signifies making a unique or unconventional choice in life. It highlights the theme of individualism and non-conformity, suggesting that the speaker's choice has had a significant impact on their life journey."
                        }
                    ]
                }
            }
        ]
        
        for c_data in poetry_content_data:
            Content.objects.get_or_create(
                module=modules['Unit 1: Poetry Analysis'],
                title=c_data['title'],
                defaults={
                    'content_type': c_data['content_type'],
                    'order': c_data['order'],
                    'text_content': c_data['text_content'],
                    'questions': c_data['questions'],
                    'estimated_minutes': 20
                }
            )
            self.stdout.write(f"Ensured content: {c_data['title']}")

        # Unit 2: Prose
        prose_content_data = [
            {
                'title': 'The Last Leaf - Excerpt',
                'content_type': 'text',
                'order': 1,
                'text_content': """In a little district west of Washington Square the streets have run crazy and broken themselves into small strips called "places." These "places" make strange angles and curves. One street crosses itself a time or two. An artist once discovered a valuable possibility in this street. Suppose a collector with a bill for paints, paper and canvas should, in traversing this route, suddenly meet himself coming back, without a cent having been paid on account!

So, to quaint old Greenwich Village the art people soon came prowling, hunting for north windows and eighteenth-century gables and Dutch attics and low rents. Then they imported some pewter mugs and a chafing dish or two from Sixth Avenue, and became a "colony." """,
                'questions': {
                    'type': 'descriptive',
                    'items': [
                        {
                            'id': 1,
                            'question': "How does the author describe the streets in the district west of Washington Square?",
                            'reference_answer': "The author describes the streets as having 'run crazy' and broken into small strips called 'places' with strange angles and curves. One street even crosses itself. This description emphasizes the chaotic, confusing, and quaint nature of the neighborhood."
                        },
                        {
                            'id': 2,
                            'question': "Why did art people come to Greenwich Village according to the text?",
                            'reference_answer': "Art people came to Greenwich Village hunting for specific architectural features like north windows, eighteenth-century gables, Dutch attics, and importantly, for low rents."
                        }
                    ]
                }
            }
        ]

        for c_data in prose_content_data:
            Content.objects.get_or_create(
                module=modules['Unit 2: Prose Comprehension'],
                title=c_data['title'],
                defaults={
                    'content_type': c_data['content_type'],
                    'order': c_data['order'],
                    'text_content': c_data['text_content'],
                    'questions': c_data['questions'],
                    'estimated_minutes': 20
                }
            )
            self.stdout.write(f"Ensured content: {c_data['title']}")
            
        self.stdout.write(self.style.SUCCESS('Successfully set up English Comprehension Course'))

