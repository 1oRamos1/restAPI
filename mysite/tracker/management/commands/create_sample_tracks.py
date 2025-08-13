from django.core.management.base import BaseCommand
from django.core.management.base import BaseCommand
from tracker.models import Category, LearningTrack  # Adjust app name if needed

class Command(BaseCommand):
    help = "Create diverse categories and IDE-only practice learning tracks"

    def handle(self, *args, **kwargs):
        languages_categories_tracks = {
            "python": [
                {
                    "category": "Web Development",
                    "tracks": [
                        {"title": "Flask Basics", "level": "beginner"},
                        {"title": "Django Fundamentals", "level": "beginner"},
                        {"title": "Flask REST APIs", "level": "advanced"},
                        {"title": "Django Advanced Patterns", "level": "advanced"},
                        {"title": "Full-stack Python Projects", "level": "master"},
                        {"title": "Asynchronous Python with FastAPI", "level": "master"},
                    ],
                },
                {
                    "category": "Data Science",
                    "tracks": [
                        {"title": "Python for Data Analysis", "level": "beginner"},
                        {"title": "Pandas and NumPy Basics", "level": "beginner"},
                        {"title": "Machine Learning with Scikit-Learn", "level": "advanced"},
                        {"title": "Data Visualization with Matplotlib & Seaborn", "level": "advanced"},
                        {"title": "Deep Learning with TensorFlow", "level": "master"},
                        {"title": "Natural Language Processing", "level": "master"},
                    ],
                },
                {
                    "category": "Automation",
                    "tracks": [
                        {"title": "Basic Python Scripting", "level": "beginner"},
                        {"title": "File Handling Automation", "level": "beginner"},
                        {"title": "Web Scraping with BeautifulSoup", "level": "advanced"},
                        {"title": "Selenium Browser Automation", "level": "advanced"},
                        {"title": "API Automation with Requests and Asyncio", "level": "master"},
                        {"title": "Build a Chatbot with Python", "level": "master"},
                    ],
                },
                {
                    "category": "Game Development",
                    "tracks": [
                        {"title": "Pygame Basics", "level": "beginner"},
                        {"title": "2D Game Mechanics", "level": "beginner"},
                        {"title": "Game Physics and Collision", "level": "advanced"},
                        {"title": "AI in Games", "level": "advanced"},
                        {"title": "Procedural Content Generation", "level": "master"},
                        {"title": "Multiplayer Game Networking", "level": "master"},
                    ],
                },
                {
                    "category": "Scripting & Utilities",
                    "tracks": [
                        {"title": "Command Line Tools", "level": "beginner"},
                        {"title": "Text Processing with Regex", "level": "beginner"},
                        {"title": "Advanced Logging and Debugging", "level": "advanced"},
                        {"title": "Packaging Python Projects", "level": "advanced"},
                        {"title": "Building Custom Python Libraries", "level": "master"},
                        {"title": "Metaprogramming and Decorators", "level": "master"},
                    ],
                },
                {
                    "category": "Data Structures & Algorithms",
                    "tracks": [
                        {"title": "Basic Data Structures in Python", "level": "beginner"},
                        {"title": "Sorting and Searching", "level": "beginner"},
                        {"title": "Graph Algorithms", "level": "advanced"},
                        {"title": "Dynamic Programming", "level": "advanced"},
                        {"title": "Algorithm Optimization Techniques", "level": "master"},
                        {"title": "Competitive Programming Challenges", "level": "master"},
                    ],
                },
            ],

            "js": [
                {
                    "category": "Frontend Basics",
                    "tracks": [
                        {"title": "JavaScript Syntax and Basics", "level": "beginner"},
                        {"title": "DOM Manipulation", "level": "beginner"},
                        {"title": "ES6+ Features", "level": "advanced"},
                        {"title": "Event Handling and Async JS", "level": "advanced"},
                        {"title": "React Fundamentals", "level": "master"},
                        {"title": "State Management with Redux", "level": "master"},
                    ],
                },
                {
                    "category": "Backend with Node.js",
                    "tracks": [
                        {"title": "Node.js Basics", "level": "beginner"},
                        {"title": "Express.js Fundamentals", "level": "beginner"},
                        {"title": "Building REST APIs", "level": "advanced"},
                        {"title": "Authentication & Authorization", "level": "advanced"},
                        {"title": "GraphQL APIs", "level": "master"},
                        {"title": "Microservices with Node.js", "level": "master"},
                    ],
                },
                {
                    "category": "Fullstack Development",
                    "tracks": [
                        {"title": "JavaScript with HTML/CSS", "level": "beginner"},
                        {"title": "Frontend & Backend Integration", "level": "beginner"},
                        {"title": "Next.js Basics", "level": "advanced"},
                        {"title": "Server-side Rendering", "level": "advanced"},
                        {"title": "Progressive Web Apps", "level": "master"},
                        {"title": "Advanced Fullstack Architectures", "level": "master"},
                    ],
                },
                {
                    "category": "Testing & Tooling",
                    "tracks": [
                        {"title": "Unit Testing with Jest", "level": "beginner"},
                        {"title": "Debugging in DevTools", "level": "beginner"},
                        {"title": "End-to-End Testing", "level": "advanced"},
                        {"title": "Performance Optimization", "level": "advanced"},
                        {"title": "CI/CD Pipelines", "level": "master"},
                        {"title": "Custom Build Tools", "level": "master"},
                    ],
                },
                {
                    "category": "Functional Programming",
                    "tracks": [
                        {"title": "Functional JS Basics", "level": "beginner"},
                        {"title": "Immutability and Pure Functions", "level": "beginner"},
                        {"title": "Advanced Functional Concepts", "level": "advanced"},
                        {"title": "Monads and Functors", "level": "advanced"},
                        {"title": "Functional Reactive Programming", "level": "master"},
                        {"title": "TypeScript for Functional JS", "level": "master"},
                    ],
                },
                {
                    "category": "Data Structures & Algorithms",
                    "tracks": [
                        {"title": "Basic Data Structures in JS", "level": "beginner"},
                        {"title": "Sorting and Searching", "level": "beginner"},
                        {"title": "Graph Algorithms", "level": "advanced"},
                        {"title": "Dynamic Programming", "level": "advanced"},
                        {"title": "Algorithm Optimization Techniques", "level": "master"},
                        {"title": "Competitive Programming Challenges", "level": "master"},
                    ],
                },
            ],

            "c++": [
                {
                    "category": "Fundamentals",
                    "tracks": [
                        {"title": "C++ Syntax Basics", "level": "beginner"},
                        {"title": "Control Structures", "level": "beginner"},
                        {"title": "Pointers and References", "level": "advanced"},
                        {"title": "Object-Oriented Programming", "level": "advanced"},
                        {"title": "Templates and Generics", "level": "master"},
                        {"title": "Memory Management", "level": "master"},
                    ],
                },
                {
                    "category": "STL & Algorithms",
                    "tracks": [
                        {"title": "Standard Template Library Basics", "level": "beginner"},
                        {"title": "Containers and Iterators", "level": "beginner"},
                        {"title": "Sorting and Searching", "level": "advanced"},
                        {"title": "Graph Algorithms", "level": "advanced"},
                        {"title": "Advanced STL Usage", "level": "master"},
                        {"title": "Competitive Programming Challenges", "level": "master"},
                    ],
                },
                {
                    "category": "Systems Programming",
                    "tracks": [
                        {"title": "File I/O", "level": "beginner"},
                        {"title": "Multithreading Basics", "level": "beginner"},
                        {"title": "Concurrency and Locks", "level": "advanced"},
                        {"title": "Low-level Memory Management", "level": "advanced"},
                        {"title": "Kernel Module Development", "level": "master"},
                        {"title": "Embedded Systems Programming", "level": "master"},
                    ],
                },
                {
                    "category": "Game Development",
                    "tracks": [
                        {"title": "Simple 2D Game Engine", "level": "beginner"},
                        {"title": "Game Loop and Input Handling", "level": "beginner"},
                        {"title": "Physics and Collision Detection", "level": "advanced"},
                        {"title": "AI in Games", "level": "advanced"},
                        {"title": "3D Graphics Programming", "level": "master"},
                        {"title": "Multiplayer Networking", "level": "master"},
                    ],
                },
                {
                    "category": "Optimization & Performance",
                    "tracks": [
                        {"title": "Profiling Basics", "level": "beginner"},
                        {"title": "Code Optimization Techniques", "level": "beginner"},
                        {"title": "Cache Optimization", "level": "advanced"},
                        {"title": "Parallel Programming", "level": "advanced"},
                        {"title": "Advanced Compiler Techniques", "level": "master"},
                        {"title": "Real-time Systems", "level": "master"},
                    ],
                },
                {
                    "category": "Advanced C++ Concepts",
                    "tracks": [
                        {"title": "Modern C++ Features", "level": "beginner"},
                        {"title": "Lambda Expressions", "level": "beginner"},
                        {"title": "Template Metaprogramming", "level": "advanced"},
                        {"title": "Concurrency Patterns", "level": "advanced"},
                        {"title": "Design Patterns", "level": "master"},
                        {"title": "Reflection and Introspection", "level": "master"},
                    ],
                },
            ],
        }

        for lang, categories in languages_categories_tracks.items():
            for cat_data in categories:
                cat_name = cat_data['category']
                tracks = cat_data['tracks']

                category, created = Category.objects.get_or_create(
                    name=cat_name,
                    defaults={'language': lang}
                )
                if not created and category.language != lang:
                    category.language = lang
                    category.save()
                self.stdout.write(f"{'Created' if created else 'Exists'} category: {cat_name} ({lang})")

                for track_data in tracks:
                    title = track_data['title']
                    level = track_data['level']

                    track, created = LearningTrack.objects.get_or_create(
                        title=title,
                        category=category,
                        defaults={'level': level},
                    )
                    if not created:
                        updated = False
                        if track.level != level:
                            track.level = level
                            updated = True
                        if track.category != category:
                            track.category = category
                            updated = True
                        if updated:
                            track.save()
                            self.stdout.write(f"Updated track: {title}")
                    else:
                        self.stdout.write(f"Created track: {title}")

