from datetime import datetime
from tempfile import TemporaryDirectory

import pytest
import pandas as pd

import process
from process import Datagroup


def _dt2ts(dt):
    timestamp = int((dt - datetime(1970, 1, 1)).total_seconds())
    return timestamp


def test_split_data_by_datetime():
    df = pd.DataFrame({'dummy': ['A', 'B', 'C'],
                       'timestamp': list(map(_dt2ts,
                                             [datetime(2000, 1, 1),
                                              datetime(2005, 1, 1),
                                              datetime(2010, 1, 1)]))})
    cut_dt = datetime(2005, 1, 1)
    expect_df_before = pd.DataFrame({'dummy': ['A', ],
                                     'timestamp': list(map(_dt2ts, [datetime(2000, 1, 1), ]))})
    expect_df_after = pd.DataFrame({'dummy': ['B', 'C', ],
                                    'timestamp': list(map(_dt2ts, [datetime(2005, 1, 1),
                                                                   datetime(2010, 1, 1), ]))})
    df_before, df_after = process.split_data_by_datetime(df, cut_dt)
    pd.testing.assert_frame_equal(df_before, expect_df_before)
    pd.testing.assert_frame_equal(df_after, expect_df_after)


def test_split_data_by_year():
    df = pd.DataFrame({'dummy': ['A', 'B', 'C'],
                       'year': [2000, 2005, 2010]})
    cut_year = 2005
    expect_df_before = pd.DataFrame({'dummy': ['A', ],
                                     'year': [2000, ]})
    expect_df_after = pd.DataFrame({'dummy': ['B', 'C', ],
                                    'year': [2005, 2010]})
    df_before, df_after = process.split_data_by_year(df, cut_year)
    pd.testing.assert_frame_equal(df_before, expect_df_before)
    pd.testing.assert_frame_equal(df_after, expect_df_after)


def test_select_data_by_movie_group():
    df = pd.DataFrame({'dummy': ['A', 'B', 'C'],
                       'movieId': [1, 2, 3]})
    movie_group = [2, 3]
    expect_df = pd.DataFrame({'dummy': ['B', 'C', ], 'movieId': [2, 3, ]})
    df = process.select_data_by_movie_group(df, movie_group)
    pd.testing.assert_frame_equal(df, expect_df)


@pytest.fixture
def datagroup():
    return Datagroup(ratings=pd.DataFrame({'userId': [1, 2, 3],
                                           'movieId': [101, 102, 103],
                                           'rating': [5, 4, 3],
                                           'timestamp': [1112486027, 1112484727, 1094785740]}),
                     tags=pd.DataFrame({'userId': [1, 2, 2],
                                        'movieId': [101, 102, 103],
                                        'tag': ['Mark Waters', 'New Zealand', 'surreal']}),
                     movies=pd.DataFrame({'movieId': [101, 102, 103],
                                          'title': ['A', 'B', 'C'],
                                          'genres': [['Drama', 'Fantasy', 'Romance'],
                                                     ['Drama', ],
                                                     ['Fantasy', 'Romance']],
                                          'year': [2010, 2014, 2009]}),
                     genome=pd.DataFrame({'movieId': [101, 102, 103],
                                          'tagId': [1001, 1001, 1001],
                                          'relevance': [0.5, 0.4, 0.9],
                                          'tag': ['yc', 'yc', 'yc']}),
                     )


def test_save_and_load_datagroup(datagroup):
    with TemporaryDirectory(dir='tmp') as temp_dir:
        process.save_datagroup(temp_dir, datagroup, 'test')
        reload_datagroup = process.load_datagroup(temp_dir, 'test')
        pd.testing.assert_frame_equal(datagroup.ratings, reload_datagroup.ratings)
        pd.testing.assert_frame_equal(datagroup.tags, reload_datagroup.tags)
        pd.testing.assert_frame_equal(datagroup.movies, reload_datagroup.movies)
        pd.testing.assert_frame_equal(datagroup.genome, reload_datagroup.genome)
