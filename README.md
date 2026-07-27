# US-AI-Water-Analysis
This study presents the seasonal and localized reshwater stress caused by AI growth under different SSP-RCP sceanarios. The following contents are included in this repository to support our key findings:
1. Codes: include an example code to conduct the estimation process.
2. Data: include all data used during the analysis.

## Requirements
To run the codes in this repository, the following Python and core packages must be installed (version is given for refenrence):
- Python 3.11.15
- numpy 2.4.4
- pandas 3.0.3
- openpyxl: 3.1.5

The above packages can be conveniently downloaded through open-source library on a normal computer. There is no specific computing resource requirements to run the main codes, which can be runned on normal computer within a few seconds.

## Codes
- **Water Stress Calculation.ipynb**: This notebook provides a computation demonstration of the project water-stress workflow. It loads the data resources, simulates monthly freshwater stress for each HUC8 under three SSP–RCP pathways and four AI cases, and prints selected national and HUC8-level results.

## Data
- **AI_Power_Water_Usage xlsx files**: Electrciity consumption and water withdrawal data of AI data centers in each HUC8 subbasin.
- **IR_HUC8_Tot_WD_monthly csv files**: Water withdrawal data of the irrigation sector in each HUC8 subbasin.
- **PS_HUC8_H08_projected csv files**: Water withdrawal data of the public supply sector in each HUC8 subbasin.
- **TPWW_HUC8_SSP2_HE2 (Baseline) xlsx files**: Water withdrawal data of the thermoelectric sector (baseline case) in each HUC8 subbasin.
- **TPWW_HUC8_SSP2_HE2 (allair) xlsx files**: Water withdrawal data of the thermoelectric sector (air-based heat rejection case) in each HUC8 subbasin.
- **ssp folders**: The freshwater availability data under different SSP-RCP sceanrios are included in these folders.
- **Air-based Heat Rejection folder**: AI_Power_Water_Usage xlsx files for the air-based heat rejection case.
- **Waste Heat Reuse folder**: AI_Power_Water_Usage xlsx files for the waste heat reuse case.

## Running the code
Download all data in the github repo, replace the BASE_PATH in the notebook with the data save path, and run the notebook code with listed packages.

## Citation
Please use the following citation when using the data, methods or results of this work:

Xiao, T. & You, F. (2026). Localized and seasonal freshwater stress amplification from U.S. AI data center growth under climate–socioeconomic pathways. Submitted to Nature Sustainability.

