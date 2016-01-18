"""Tests for functions in king.py."""
import puget.king as pk
import puget
import os.path as op
import pandas as pd
import pandas.util.testing as pdt
import numpy as np
import tempfile
import json
from nose import with_setup


def test_read_table():
    """Test read_table function."""
    # create temporary csv file
    temp_csv_file = tempfile.NamedTemporaryFile(mode='w')
    df = pd.DataFrame({'id': [1, 1, 2, 2],
                       'time1': ['2001-01-13', '2004-05-21', '2003-06-10',
                                 '2003-06-10'], 'drop1': [2, 3, 4, 5],
                       'ig_dedup1': [5, 6, 7, 8], 'categ1': [0, 8, 0, 0]})
    df.to_csv(temp_csv_file)
    temp_csv_file.seek(0)

    file_dict = {2011: temp_csv_file.name}
    df = pk.read_table(file_dict, columns_to_drop=['drop1'],
                       categorical_var=['categ1'], time_var=['time1'],
                       duplicate_check_columns=['id', 'time1', 'categ1'])
    df_test = pd.DataFrame({'Unnamed: 0': [0, 1, 3], 'id': [1, 1, 2],
                            'time1':
                            pd.to_datetime(['2001-01-13', '2004-05-21',
                                            '2003-06-10'], errors='coerce'),
                            'ig_dedup1': [5, 6, 8], 'categ1': [0, np.nan, 0],
                            'years': [2011, 2011, 2011]})
    # Have to change the index to match the one we de-duplicated
    df_test.index = pd.Int64Index([0, 1, 3])
    pdt.assert_frame_equal(df, df_test)

    temp_csv_file.close()


def test_get_enrollment():
    """Test get_enrollment function."""
    # create temporary csv file & metadata file to read in
    temp_csv_file = tempfile.NamedTemporaryFile(mode='w')
    temp_meta_file = tempfile.NamedTemporaryFile(mode='w')
    df = pd.DataFrame({'id': [1, 1, 2, 2],
                       'time1': ['2001-01-13', '2004-05-21', '2003-06-10',
                                 '2003-06-10'], 'drop1': [2, 3, 4, 5],
                       'ig_dedup1': [5, 6, 7, 8], 'categ1': [0, 8, 0, 0]})
    df.to_csv(temp_csv_file)
    temp_csv_file.seek(0)

    metadata = ({'name': 'test',
                 'duplicate_check_columns': ['id', 'time1', 'categ1'],
                 'columns_to_drop': ['drop1'],
                 'categorical_var': ['categ1'], 'time_var': ['time1']})
    metadata_json = json.dumps(metadata)
    temp_meta_file.file.write(metadata_json)
    temp_meta_file.seek(0)

    file_dict = {2011: temp_csv_file.name}

    # first try with groups=True (default)
    df = pk.get_enrollment(file_dict=file_dict,
                           metadata_file=temp_meta_file.name,
                           groupID_column='id')

    df_test = pd.DataFrame({'Unnamed: 0': [0, 1], 'id': [1, 1], 'time1':
                            pd.to_datetime(['2001-01-13', '2004-05-21'],
                            errors='coerce'), 'ig_dedup1': [5, 6],
                            'categ1': [0, np.nan],
                            'years': [2011, 2011]})
    pdt.assert_frame_equal(df, df_test)

    # try again with groups=False
    df = pk.get_enrollment(groups=False, file_dict=file_dict,
                           metadata_file=temp_meta_file.name,
                           groupID_column='id')

    df_test = pd.DataFrame({'Unnamed: 0': [0, 1, 3], 'id': [1, 1, 2],
                            'time1':
                            pd.to_datetime(['2001-01-13', '2004-05-21',
                                            '2003-06-10'], errors='coerce'),
                                'ig_dedup1': [5, 6, 8],
                                'categ1': [0, np.nan, 0],
                                'years': [2011, 2011, 2011]})
    # Have to change the index to match the one we de-duplicated
    df_test.index = pd.Int64Index([0, 1, 3])
    pdt.assert_frame_equal(df, df_test)

    temp_csv_file.close()
    temp_meta_file.close()


def test_get_exit():
    """test get_exit function."""
    # create temporary csv file & metadata file to read in
    temp_csv_file = tempfile.NamedTemporaryFile(mode='w')
    temp_meta_file = tempfile.NamedTemporaryFile(mode='w')
    dest_rand_ints = np.random.random_integers(1, 30, 3)
    df_init = pd.DataFrame({'id': [11, 12, 13], 'dest': dest_rand_ints})
    df_init.to_csv(temp_csv_file)
    temp_csv_file.seek(0)

    metadata = ({'name': 'test', 'duplicate_check_columns': ['id']})
    metadata_json = json.dumps(metadata)
    temp_meta_file.file.write(metadata_json)
    temp_meta_file.seek(0)

    file_dict = {2011: temp_csv_file.name}

    df = pk.get_exit(file_dict=file_dict, metadata_file=temp_meta_file.name,
                     df_destination_colname='dest')

    mapping_table = pd.read_csv(op.join(puget.data.DATA_PATH, 'metadata',
                                        'destination_mappings.csv'))

    map_table_test_ints = [2, 25, 26]
    map_table_test = pd.DataFrame({'Standard': np.array(['New Standards']*3),
                                   'DestinationNumeric': np.array(
                                        map_table_test_ints).astype(float),
                                   'DestinationDescription': ['Transitional housing for homeless persons (including homeless youth)',
                                                              'Long-term care facility or nursing home',
                                                              'Moved from one HOPWA funded project to HOPWA PH'],
                                   'DestinationGroup': ['Temporary',
                                                        'Permanent',
                                                        'Permanent'],
                                   'DestinationSuccess': ['Other Exit',
                                                          'Successful Exit',
                                                          'Successful Exit'],
                                   'Subsidy': ['No', 'No', 'Yes']})

    map_table_subset = mapping_table[mapping_table['DestinationNumeric'] ==
                                     map_table_test_ints[0]]
    map_table_subset = map_table_subset.append(mapping_table[
        mapping_table['DestinationNumeric'] == map_table_test_ints[1]])
    map_table_subset = map_table_subset.append(mapping_table[
        mapping_table['DestinationNumeric'] == map_table_test_ints[2]])
    # Have to change the index to match the one we made up
    map_table_subset.index = pd.Int64Index([0, 1, 2])

    # sort because column order is not assured because started with dicts
    map_table_test = map_table_test.sort_index(axis=1)
    map_table_subset = map_table_subset.sort_index(axis=1)

    pdt.assert_frame_equal(map_table_subset, map_table_test)

    mapping_table = mapping_table[mapping_table.Standard == 'New Standards']
    mapping_table['Subsidy'] = mapping_table['Subsidy'].map({'Yes': True,
                                                             'No': False})
    mapping_table = mapping_table.drop(['Standard'], axis=1)
    mapping_table

    df_test = pd.DataFrame({'Unnamed: 0': [0, 1, 2], 'id': [11, 12, 13],
                            'years': [2011, 2011, 2011],
                            'dest': dest_rand_ints})
    df_test = pd.merge(left=df_test, right=mapping_table, how='left',
                       left_on='dest', right_on='DestinationNumeric')
    df_test = df_test.drop('dest', axis=1)

    pdt.assert_frame_equal(df, df_test)

    temp_csv_file.close()
    temp_meta_file.close()


def test_get_client():
    # TODO: test more parts of get_client

    # create temporary csv files & metadata file to read in
    # need to make a temporary directory because of assumed directory
    #  structure in read_table
    temp_csv_file1 = tempfile.NamedTemporaryFile(mode='w')
    temp_csv_file2 = tempfile.NamedTemporaryFile(mode='w')
    df_init = pd.DataFrame({'id': [11, 12],
                            'dob_col': ['1990-01-13', '2012-05-21']})
    df2_init = pd.DataFrame({'id': [11, 12],
                             'dob_col': ['1990-01-13', '2012-05-21']})
    df_init.to_csv(temp_csv_file1)
    temp_csv_file1.seek(0)
    df2_init.to_csv(temp_csv_file2)
    temp_csv_file2.seek(0)

    years = [2011, 2013]
    file_dict = dict(zip(years, [temp_csv_file1.name, temp_csv_file2.name]))

    temp_meta_file = tempfile.NamedTemporaryFile(mode='w')
    metadata = ({'name': 'test', 'duplicate_check_columns': ['id'],
                 'time_var': ['dob_col'], 'pid_column': ['id']})
    metadata_json = json.dumps(metadata)
    temp_meta_file.file.write(metadata_json)
    temp_meta_file.seek(0)

    # get path & filenames
    df = pk.get_client(file_dict=file_dict, years=years,
                       metadata_file=temp_meta_file.name,
                       dob_colname='dob_col')

    df_test = pd.DataFrame({'Unnamed: 0': [0, 1], 'id': [11, 12],
                            'dob_col': ['1990-01-13', pd.NaT]})

    # Have to change the index to match the one we de-duplicated
    df_test.index = pd.Int64Index([2, 3])
    pdt.assert_frame_equal(df, df_test)

    temp_csv_file1.close()
    temp_csv_file2.close()
    temp_meta_file.close()
