import pandas as pd

from resource.constants import accident_dataset, ohio_accident_dataset, hospital_dataset, ohio_hospital_dataset_csv

#accident_df = pd.read_csv(accident_dataset, nrows=600)
#pd.DataFrame(accident_df).to_csv(ohio_accident_dataset)

hospital_dataset = pd.read_csv(hospital_dataset)
ohio_hospital_dataset = hospital_dataset[hospital_dataset['STATE'] == 'OH']
ohio_hos_dataset_dataframe = pd.DataFrame(ohio_hospital_dataset)
ohio_hos_dataset_dataframe.to_csv(ohio_hospital_dataset_csv)

