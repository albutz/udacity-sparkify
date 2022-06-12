"""ETL pipeline."""
from pathlib import Path

from sqlalchemy.future.engine import Engine
from tqdm import tqdm

from read import get_file_paths, read_h5
from tables import artist_table_init, song_table_init
from utils import cast_numeric, encode_str


def run_initial_pipeline(engine: Engine) -> None:
    """Initial ETL pipeline.

    Minimal processing to load songs and artists into the database.

    Args:
        engine: Engine to connect to the database
    """
    file_paths = get_file_paths(Path("data"))

    for file_path in tqdm(file_paths):

        # Load individual file
        song_df = read_h5(file_path)
        song_df = song_df.apply(lambda ser: ser.where(~ser.isnull(), None))

        # Insert artist
        # fmt: off
        insert_artist_stmt = (
            artist_table_init.
            insert().
            values(
                name=encode_str(song_df.artist_name),
                location=encode_str(song_df.artist_location),
                latitude=cast_numeric(song_df.artist_latitude),
                longitude=cast_numeric(song_df.artist_longitude)
            )
        )
        # fmt: on

        with engine.connect() as conn:
            conn.execute(insert_artist_stmt)
            conn.commit()

        # Insert song
        # fmt:off
        insert_song_stmt = (
            song_table_init.
            insert().
            values(
                title=encode_str(song_df.title),
                year=cast_numeric(song_df.year),
                danceability=cast_numeric(song_df.danceability),
                duration=cast_numeric(song_df.duration),
                end_of_fade_in=cast_numeric(song_df.end_of_fade_in),
                start_of_fade_out=cast_numeric(song_df.start_of_fade_out),
                loudness=cast_numeric(song_df.loudness),
                bpm=cast_numeric(song_df.tempo),
                album_name=encode_str(song_df.release),
                artist_name=encode_str(song_df.artist_name),
            )
        )
        # fmt: on

        with engine.connect() as conn:
            conn.execute(insert_song_stmt)
            conn.commit()
