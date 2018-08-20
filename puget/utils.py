import pandas as pd
import os.path as op
import numpy as np
from puget.data import DATA_PATH
from dateutil.parser import parse as parse_date

METADATA = op.join(DATA_PATH, 'metadata')


def merge_destination(df, df_destination_column='destination_value',
                      destination_map_fname='destination_mappings.csv',
                      directory=METADATA):
    """
    Merge a categorization of destination outcomes into a dataframe using
    the column of numeric destination outcomes as the merge-by variable.

    Parameters
    -----------
    df: a dataframe with a column that contains the numeric destination
        outcomes

    df_destination_column: a string - the name of the column that contains the
        numeric destination outcomes

    destination_map_fname: string (optional). The filename containing the
        categorization of destination outcomes. The default is
        destination_mappings.csv in the metadata directory

    directory: string (optional). The directory containing the mapping file.

    Returns
    -------
    output_df: A pandas dataframe containing the original dataframe, plus 4 new
        columns with the mappings for destination. The new columns are :
        DestinationDescription:  Text description of destination
        DestinationGroup : it is more aggregated than DestinationDescription,
            but less than DestinationSuccess
        DestinationSuccess : a binary : two values are  'Other Exit',
            'Successful Exit' (or 'NaN')
        success_and_subsidy: a column with three possible values -- successful
            with & without subsidy, unsuccessful
        Subsidy
    """
    # Import the csv file into pandas:
    mapping_table = pd.read_csv(op.join(directory, destination_map_fname))
    mapping_table = mapping_table[mapping_table.Standard == "New Standards"]
    # Recode Subsidy column to boolean
    mapping_table['Subsidy'] = mapping_table['Subsidy'].map({'Yes': True,
                                                             'No': False})
    # Drop columns we don't need
    mapping_table = mapping_table.drop(['Standard'], axis=1)

    # Merge the Destination mapping with the df
    # based on the last_destination string
    output_df = pd.merge(left=df, right=mapping_table, how='left',
                         left_on=df_destination_column,
                         right_on='DestinationNumeric')

    output_df = output_df.drop(df_destination_column, axis=1)

    return output_df


def update_progress(progress):
    """Progress bar in the console.
    Inspired by
    http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    Parameters
    -----------
    progress : a value (float or int) between 0 and 100 indicating
               percentage progress
    """
    print('\r[%-10s] %0.2f%%' % ('#' * int(progress/10), progress))
    


def normalize_ssn(row, ssn_col="SSN"):
    """ 
    Normalize a SSN column. 
    
    This function normalizes towards a string made from an integer of form:
    
    "1234567"
    
    Removing dashes (e.g. "123-456-789") or floats (e.g., "123456789.0").
    
    """
    try:
        return str(int(row[ssn_col]))
    except:
        try: 
            return str(int(''.join(row[ssn_col].split('-'))))
        except: 
            return None

        
def normalize_dates(row, date_col="DOB"):
    """ 
    Normalize a date column 
    
    Returns `parse_date` on each item in the column and None 
    when an item cannot be parsed this way.
    """
    try:
        return parse_date(row[date_col])
    except:
        return None
    

def compare_on_column(df1, df2, column):
    """
    Compare two data frames in terms of value counts on `column`.
    """
    comparison = pd.DataFrame(dict(df1=df1[column].value_counts(normalize=True),
                                   df2=df2[column].value_counts(normalize=True)))
    return comparison


def normalize_names(row, name_col=""):  
    return str(row[name_col]).upper()
    
  
    print('\r[%-10s] %0.2f%%' % ('#' * int(progress / 10), progress))


def clean_ssn(ssn):
    """
    Clean up corner cases for SSN values
    """
    # First case, SSN is 11111111, 22222222, etc.:
    nulls = [11111111 * i for i in range(1, 9)]
    if ssn in nulls:
        return np.nan
    # There might be some other conditions here.
    else:
        return ssn


def stringify_ssn(ssn):
    """
    Create a string variable based on an SSN variable
    """
    if pd.isnull(ssn):
        return None
    else:
        ssn_str = str(int(ssn))
        return ssn_str