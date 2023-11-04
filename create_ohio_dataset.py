import pandas as pd

from resource.constants import accident_dataset, ohio_accident_dataset

accident_df = pd.read_csv(accident_dataset, nrows=600)
pd.DataFrame(accident_df).to_csv(ohio_accident_dataset)
