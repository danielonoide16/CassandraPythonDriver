from gevent import monkey
monkey.patch_all()
from cassandra.cluster import Cluster

# ==============================
# CQL Statements
# ==============================
CREATE_KEYSPACE = "CREATE KEYSPACE IF NOT EXISTS movies WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}"
CREATE_TABLE_MOVIE_BY_TITLE = """
CREATE TABLE IF NOT EXISTS movies.movie_by_title (
    movie_id uuid,
    title text,
    release_year int,
    genre text, 
    rating float,
    director text,
    PRIMARY KEY (title, release_year)
)
"""
CREATE_TABLE_MOVIE_BY_GENRE = """
CREATE TABLE IF NOT EXISTS movies.movie_by_genre (
    movie_id uuid,
    title text,
    release_year int,
    genre text, 
    rating float,
    director text,
    PRIMARY KEY (genre, rating)
) WITH CLUSTERING ORDER BY (rating DESC);
"""
INSERT_MOVIE_TITLE = """
INSERT INTO movies.movie_by_title (movie_id, title, release_year, genre, rating, director)
VALUES (%s, %s, %s, %s, %s, %s)
"""
INSERT_MOVIE_GENRE = """
INSERT INTO movies.movie_by_genre (movie_id, title, release_year, genre, rating, director)
VALUES (%s, %s, %s, %s, %s, %s)
"""
DELETE_MOVIE_TITLE = """
DELETE FROM movies.movie_by_title WHERE title = ? AND release_year = ?
"""
DELETE_MOVIE_GENRE = """
DELETE FROM movies.movie_by_genre WHERE genre = ? AND rating = ?
"""
SELECT_BY_TITLE = "SELECT * FROM movies.movie_by_title WHERE title = ? AND release_year = ?"
SELECT_BY_GENRE = "SELECT * FROM movies.movie_by_genre WHERE genre = ?"

# ==============================
# Funciones base
# ==============================
def create_keyspace_and_tables(session):
    session.execute(CREATE_KEYSPACE)
    session.set_keyspace("movies")
    session.execute(CREATE_TABLE_MOVIE_BY_TITLE)
    session.execute(CREATE_TABLE_MOVIE_BY_GENRE)
    print("Keyspace y tablas creadas")
    

def insert_movie(session, title, year, director, genre, rating):
    import uuid
    movie_id = uuid.uuid4()
    session.execute(INSERT_MOVIE_TITLE, (movie_id, title, year, genre, rating, director))
    session.execute(INSERT_MOVIE_GENRE, (movie_id, title, year, genre, rating, director))
    print(f"Película '{title}' insertada en la base de datos")

def query_by_title(session, title, year):
    statement = session.prepare(SELECT_BY_TITLE)
    rows = session.execute(statement, (title, year))
    for row in rows:
        print(f"Title: {row.title}, Year: {row.release_year}, Genre: {row.genre}, Rating: {row.rating}, Director: {row.director}")

def query_by_genre(session, genre):
    statement = session.prepare(SELECT_BY_GENRE)
    rows = session.execute(statement, (genre,))
    for row in rows:
        print(f"Title: {row.title}, Year: {row.release_year}, Genre: {row.genre}, Rating: {row.rating}, Director: {row.director}")

def update_movie_director(session, title, release_year, genre, rating, new_director):
    # Actualizar director en movie_by_title
    update_title_query = """
    UPDATE movies.movie_by_title
    SET director = ?
    WHERE title = ? AND release_year = ?
    """
    statement_title = session.prepare(update_title_query)
    session.execute(statement_title, (new_director, title, release_year))

    # Actualizar director en movie_by_genre
    update_genre_query = """
    UPDATE movies.movie_by_genre
    SET director = ?
    WHERE genre = ? AND rating = ?
    """
    statement_genre = session.prepare(update_genre_query)
    session.execute(statement_genre, (new_director, genre, rating))

    print(f"Director de la película '{title}' actualizado a '{new_director}'")

def delete_movie(session, title, genre, rating, release_year):
    # Eliminar de movie_by_title
    statement_title = session.prepare(DELETE_MOVIE_TITLE)
    session.execute(statement_title, (title, release_year))

    # Eliminar de movie_by_genre
    statement_genre = session.prepare(DELETE_MOVIE_GENRE)
    session.execute(statement_genre, (genre, rating))

    print(f"Película '{title}' eliminada de la base de datos")

def delete_keyspace_and_tables(session):
    session.execute("DROP TABLE IF EXISTS movies.movie_by_title")
    session.execute("DROP TABLE IF EXISTS movies.movie_by_genre")
    session.execute("DROP KEYSPACE IF EXISTS movies")
    print("Keyspace y tablas eliminadas")

# ==============================
# Menú
# ==============================
def main():
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()

    #delete tables 
    #delete_keyspace_and_tables(session)
    create_keyspace_and_tables(session)


    while True:
        print("\n=== Movie Database Menu ===")
        print("1. Insertar película")
        print("2. Consultar por título")
        print("3. Consultar por género")
        print("4. Actualizar director")
        print("5. Eliminar película")
        print("0. Salir")
        choice = input("Seleccione opción: ")

        if choice == "1":
            title = input("Título: ")
            year = int(input("Año: "))
            director = input("Director: ")
            genre = input("Género: ")
            rating = float(input("Rating: "))
            print(title, year, director, genre, rating)
            insert_movie(session, title, year, director, genre, rating)
        elif choice == "2":
            title = input("Título: ")
            year = int(input("Año: "))
            query_by_title(session, title, year)
        elif choice == "3":
            genre = input("Género: ")
            query_by_genre(session, genre)
        elif choice == "4":
            title = input("Título: ")
            release_year = int(input("Año: "))
            genre = input("Género: ")
            rating = float(input("Rating: "))
            new_director = input("Nuevo Director: ")
            update_movie_director(session, title, release_year, genre, rating, new_director)
        elif choice == "5":
            # Eliminar de movie_by_title -> title, release_year
            # Eliminar de movie_by_genre -> genre, rating
            title = input("Título: ")
            genre = input("Género: ")
            rating = float(input("Rating: "))
            release_year = int(input("Año: "))
            delete_movie(session, title, genre, rating, release_year)
        elif choice == '0':
            #cerrar la conexión a Cassandra
            session.shutdown()
            cluster.shutdown()
            print("Conexión a Cassandra cerrada")
            print("Saliendo del programa...")
            break
        else:
            print("Opción inválida")
            break

if __name__ == "__main__":
    main()