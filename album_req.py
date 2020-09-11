import os

from bottle import route
from bottle import run
from bottle import HTTPError
from bottle import request

# импортируем библиотеку sqlalchemy и некоторые функции из нее 
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# константа, указывающая способ соединения с базой данных
DB_PATH = "sqlite:///albums.sqlite3"
# базовый класс моделей таблиц
Base = declarative_base()

class Album(Base):

    __tablename__ = 'album'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    year = sa.Column(sa.Integer)
    artist = sa.Column(sa.Text)
    genre = sa.Column(sa.Text)
    album = sa.Column(sa.Text)

    def __eq__(self, other):
        # сравнение двух объектов класса Album
        if isinstance(other, Album):
            return (self.year == other.year and
                    self.artist == other.artist and
                    self.genre == other.genre and
                    self.album == other.album)
        # иначе возвращаем NotImplemented
        return NotImplemented


def connect_db():
    """
    Устанавливает соединение к базе данных, создает таблицы, если их еще нет и возвращает объект сессии 
    """
    # создаем соединение к базе данных
    engine = sa.create_engine(DB_PATH)
    # создаем описанные таблицы
    Base.metadata.create_all(engine)
    # создаем фабрику сессию
    session = sessionmaker(engine)
    # возвращаем сессию
    return session()

def all_artists():
    # Возвращает список всех артистов из таблицы album
    list_art = []
    session = connect_db()
    albums = session.query(Album).all()
    for album in albums:
        list_art.append(album.artist + '  ')
    return set(list_art)

@route('/albums/<artist>')
def find_albums(artist):
    
    result1 = 'База содержит альбомы следующих исполнителей: {}'.format(all_artists())
    
    list_alb = []
    session = connect_db()
    # нахдим все записи в таблице Album, у которых поле Album.artist совпадает с парарметром artist
    albums = session.query(Album).filter(Album.artist == artist).all()
    # Количество альбомов заданного артиста
    quant = len(albums)
    if quant != 0:
        result = 'Количество альбомов {} равно: {}'.format(artist,str(quant))
        for alb in albums:
            list_alb.append(alb.album)
        result = result1 + '<br><br>' + result + '<br>' + 'Список альбомов <br>{} '.format(list_alb)
    else:
        message = "Альбомов '{}' не найдено".format(artist)
        result = HTTPError(404, message)
    return result


def save_album(a_data):
    # Добавление записи а таблицу
    session = connect_db()
    albums = session.query(Album).all()
    for album in albums:
        if album == a_data:
            result = HTTPError(404, message)
    session.add(a_data)
    session.commit()
    return True

# def del_album(id_):
#     session = connect_db()
#     alb = session.query(Album).filter(Album.id == id_).delete(synchronize_session=False)
#     session.commit()



def year_valid(year):
    ye = int(year)
    if ye >1000 and ye < 2021:
        return True
    return False 

@route("/albums", method="POST")
def get_data():
    year = request.forms.get("year")
    artist = request.forms.get("artist")
    genre = request.forms.get("genre")
    album = request.forms.get("album")

    if not year_valid(year):
        return "Не правильно введен год выпуска альбома"
    if len(genre) == 0:
        return "Не введен жанр"
    if len(artist) == 0:
        return "Не введено имя артиста"
    if len(album) == 0:
        return "Не введено название альбома"
    album_data = Album(
        year = int(year),
        artist = artist,
        genre = genre,
        album = album)

    if save_album(album_data):
        return "Данные успешно сохранены"
    

if __name__ == "__main__":
    run(host="localhost", port=8080, debug=True)
