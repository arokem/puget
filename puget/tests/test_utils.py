import puget.utils as pu
import puget
import os.path as op
import pandas as pd
import pandas.util.testing as pdt
import tempfile


def test_merge_destination():
    """Test merge_destination function."""
    TF = tempfile.NamedTemporaryFile(mode='w')
    df = pd.DataFrame({'Standard': ['New Standards', 'New Standards',
                                    'New Standards', 'Old Standards'],
                       'DestinationNumeric': [1, 2, 3, 4],
                       'DestinationDescription': ['Success no subsidy',
                                                  'Success with subsidy',
                                                  'Unsuccessful',
                                                  'Unsuccessful'],
                       'DestinationGroup': ['Permanent', 'Permanent',
                                            'Temporary', 'Temporary'],
                       'DestinationSuccess': ['Successful Exit',
                                              'Successful Exit',
                                              'Other Exit', 'Other Exit'],
                       'Subsidy': ['No', 'Yes', 'No', 'No']})
    df.to_csv(TF, index=False)
    TF.seek(0)

    path, fname = op.split(TF.name)
    df = pd.DataFrame({'numeric': [1, 2, 3]})
    df_merge = pu.merge_destination(df, df_destination_column='numeric',
                                    destination_map_fname=fname,
                                    directory=path)
    df_test = pd.DataFrame({'DestinationNumeric': [1, 2, 3],
                            'DestinationDescription': [
                                'Success no subsidy',
                                'Success with subsidy',
                                'Unsuccessful'],
                            'DestinationGroup': ['Permanent', 'Permanent',
                                                 'Temporary'],
                            'DestinationSuccess': ['Successful Exit',
                                                   'Successful Exit',
                                                   'Other Exit'],
                            'Subsidy': [False, True, False]})
    pdt.assert_frame_equal(df_merge, df_test)

    TF.close()

    
def test_normalize_ssn():

    df = pd.DataFrame({"SSN": ["123-456-789", 123456789.0, "*23456789"]})
    df["SSN"] = df.apply(pu.normalize_ssn, axis=1)
    df_test = pd.DataFrame({"SSN": ["123456789", "123456789", None]})
    pdt.assert_frame_equal(df, df_test)

    df = pd.DataFrame({"foo": ["123-456-789", 123456789.0, "*23456789"]})
    df["foo"] = df.apply(pu.normalize_ssn, axis=1, ssn_col="foo")
    df_test = pd.DataFrame({"foo": ["123456789", "123456789", None]})
    pdt.assert_frame_equal(df, df_test)

    
def test_normalize_dates():
    df = pd.DataFrame({"dob": [" 12/09/1977", " 12/09/1977", "foo"]})
    df["dob"] = df.apply(pu.normalize_dates, axis=1, date_col="dob")
    df_test = pd.DataFrame({"dob": [pd.Timestamp('1977-12-09 00:00:00'),
                                    pd.Timestamp('1977-12-09 00:00:00'),
                                    None]})
    pdt.assert_frame_equal(df, df_test)

    
def test_compare_on_column():
    df1 = pd.DataFrame({'col1': [1, 1, 1, 2, 2, 2], 
                       'col2': [1, 1, 2, 2, 2, 2]})
    df2 = pd.DataFrame({'col1': [1, 1, 2, 2], 
                        'col2': [1, 1, 1, 2]})
    df_compare = pu.compare_on_column(df1, df2, 'col1')
    df_test = pd.DataFrame(index=[2, 1],
                           data=dict(df1={1:0.5, 2:0.5},
                                     df2={1:0.5, 2:0.5})) 
    
    pdt.assert_frame_equal(df_compare, df_test)

    df_compare = pu.compare_on_column(df1, df2, 'col2')
    df_test = pd.DataFrame(index=[1, 2],
                           data=dict(df1={1:1/3., 2:2/3.},
                                     df2={1:0.75, 2:0.25})) 
    
    pdt.assert_frame_equal(df_compare, df_test)

    
def test_normalize_names():
    df = pd.DataFrame({"Name":["Calliope", "Clio", "Erato", 
                               "Euterpe", "Melpomene", "Polyhymnia",
                               "Terpsichore", "Thalia"]})

    df["norm_names"] = df.apply(pu.normalize_names, axis=1, name_col="Name")
    
    df["norm_names"] = pd.Series(['CALLIOPE', 'CLIO','ERATO',
                                  'EUTERPE', 'MELPOMENE', 'POLYHYMNIA',
                                  'TERPSICHORE', 'THALIA'])                           