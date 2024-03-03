import random

def RandomGreeting():
    greetings = {
        'English': ['Hello', 'Hi', 'Hey'],
        'Spanish': ['Hola', '¡Hola!', 'Buenos días'],
        'French': ['Bonjour', 'Salut', 'Coucou'],
        'German': ['Hallo', 'Guten Tag', 'Servus'],
        'Italian': ['Ciao', 'Buongiorno', 'Salve'],
        'Polish': ['Cześć', 'Witaj', 'Dzień dobry']
    }

    language = random.choice(list(greetings.keys()))
    greeting = random.choice(greetings[language])

    return f'{greeting}'