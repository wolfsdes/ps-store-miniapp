from sqlalchemy.orm import Session
from .models import Game

DEMO_GAMES = [
    {
        "title": "GTA VI",
        "platform": "PS5",
        "image": "https://images.unsplash.com/photo-1605901309584-818e25960a8f?auto=format&fit=crop&w=900&q=80",
        "description": "Криминальный экшен нового поколения. Демонстрационная карточка для MVP.",
        "price_try": 2499,
        "featured": True,
    },
    {
        "title": "EA SPORTS FC 26",
        "platform": "PS5 / PS4",
        "image": "https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?auto=format&fit=crop&w=900&q=80",
        "description": "Футбольный симулятор. Демонстрационная карточка для MVP.",
        "price_try": 2199,
        "featured": True,
    },
    {
        "title": "Ghost of Yotei",
        "platform": "PS5",
        "image": "https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=900&q=80",
        "description": "Приключенческий экшен. Демонстрационная карточка для MVP.",
        "price_try": 2899,
        "featured": True,
    },
    {
        "title": "Call of Duty: Black Ops 6",
        "platform": "PS5 / PS4",
        "image": "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=900&q=80",
        "description": "Динамичный шутер. Демонстрационная карточка для MVP.",
        "price_try": 1999,
        "featured": False,
    },
    {
        "title": "Hogwarts Legacy",
        "platform": "PS5 / PS4",
        "image": "https://images.unsplash.com/photo-1593305841991-05c297ba4575?auto=format&fit=crop&w=900&q=80",
        "description": "Приключение в мире магии. Демонстрационная карточка для MVP.",
        "price_try": 1799,
        "featured": False,
    },
    {
        "title": "Red Dead Redemption 2",
        "platform": "PS4",
        "image": "https://images.unsplash.com/photo-1603481546238-487240415921?auto=format&fit=crop&w=900&q=80",
        "description": "Большое приключение на Диком Западе. Демонстрационная карточка для MVP.",
        "price_try": 1599,
        "featured": False,
    },
    {
        "title": "Elden Ring",
        "platform": "PS5 / PS4",
        "image": "https://images.unsplash.com/photo-1619255001424-9b8a4d6a0e7c?auto=format&fit=crop&w=900&q=80",
        "description": "Фэнтезийная action RPG. Демонстрационная карточка для MVP.",
        "price_try": 1899,
        "featured": True,
    },
    {
        "title": "Spider-Man 2",
        "platform": "PS5",
        "image": "https://images.unsplash.com/photo-1608889175123-8ee362201f81?auto=format&fit=crop&w=900&q=80",
        "description": "Супергеройский экшен. Демонстрационная карточка для MVP.",
        "price_try": 2299,
        "featured": False,
    },
]

def seed_games(db: Session):
    if db.query(Game).count():
        return
    db.add_all(Game(**item) for item in DEMO_GAMES)
    db.commit()
