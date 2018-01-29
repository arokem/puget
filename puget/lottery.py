import pandas as pd
import numpy as np
import puget.utils as pu
import recordlinkage as rl


def _match_features(row):
    if row.sum() == 1:
        return False
    elif row["SSN"] == 1: 
        return True
    elif row["LastName"] == 1 and row["DOB"] == 1:
        return True
    else:
        return False
    

def link_records(df1, df2):
    """ """
    
    indexer_first_name = rl.SortedNeighbourhoodIndex(left_on="FirstName", right_on="FirstName")
    indexer_ssn = rl.SortedNeighbourhoodIndex(left_on="SSN", right_on="SSN")
    
    pairs_ssn = indexer_ssn.index(df1, df2)
    pairs_first_name = indexer_first_name.index(df1, df2)
    pairs_values = np.concatenate([pairs_ssn.values, pairs_first_name.values])
    pairs = pd.MultiIndex.from_tuples(pairs_values)
    
    compare_cl = rl.Compare()    
    compare_cl.string('LastName', 'LastName', method='levenshtein', threshold=0.85, label='LastName')
    compare_cl.string('FirstName', 'FirstName', method='levenshtein', threshold=0.85, label='FirstName')
    compare_cl.date("DOB", "DOB", label="DOB")
    compare_cl.string("SSN", "SSN",  method='levenshtein', threshold=0.85, label='SSN')
    
    features = compare_cl.compute(pairs, df1, df2)
    features["match"] = features.apply(_match_features, axis=1)

    matches = features[features["match"]]
    idx_0 = matches.reset_index()["level_0"]
    idx_1 = matches.reset_index()["level_1"]
    
    merged = pd.merge(df1.loc[idx_0].reset_index(), 
                      df2.loc[idx_1].reset_index(), 
                      left_index=True, right_index=True)

    merged = merged.drop_duplicates()
    return merged

    