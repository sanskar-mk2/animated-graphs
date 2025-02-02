Data from https://www.kaggle.com/datasets/abhisheksjha/time-series-air-quality-data-of-india-2010-2023/data

How AQI is calculated from: http://app.cpcbccr.com/ccr_docs/How_AQI_Calculated.pdf

## How is AQI calculated?

1. The Sub-indices for individual pollutants at a monitoring location are calculated using its
   24-hourly average concentration value (8-hourly in case of CO and O3) and health
   breakpoint concentration range. The worst sub-index is the AQI for that location.
2. All the eight pollutants may not be monitored at all the locations. Overall AQI is
   calculated only if data are available for minimum three pollutants out of which one should
   necessarily be either PM2.5 or PM10. Else, data are considered insufficient for calculating
   AQI. Similarly, a minimum of 16 hours’ data is considered necessary for calculating subindex.
3. The sub-indices for monitored pollutants are calculated and disseminated, even if data are
   inadequate for determining AQI. The Individual pollutant-wise sub-index will provide air
   quality status for that pollutant.
4. The web-based system is designed to provide AQI on real time basis. It is an automated
   system that captures data from continuous monitoring stations without human
   intervention, and displays AQI based on running average values (e.g. AQI at 6am on a
   day will incorporate data from 6am on previous day to the current day).
5. For manual monitoring stations, an AQI calculator is developed wherein data can be fed
   manually to get AQI value.

## Breakpoints for AQI Calculation
Link: http://www.arthapedia.in/index.php/National_Air_Quality_Index


| AQI Category (Range) | PM₁₀ 24-hr | PM₂.₅ 24-hr | NO₂ 24-hr | O₃ 8-hr | CO 8-hr (mg/m³) | SO₂ 24-hr | NH₃ 24-hr | Pb 24-hr |
|---------------------|-------------|-------------|-----------|---------|-----------------|-----------|------------|-----------|
| Good (0-50)         | 0-50        | 0-30        | 0-40      | 0-50    | 0-1.0          | 0-40      | 0-200      | 0-0.5     |
| Satisfactory (51-100)| 51-100     | 31-60       | 41-80     | 51-100  | 1.1-2.0        | 41-80     | 201-400    | 0.5-1.0   |
| Moderately polluted (101-200) | 101-250 | 61-90 | 81-180    | 101-168 | 2.1-10         | 81-380    | 401-800    | 1.1-2.0   |
| Poor (201-300)      | 251-350     | 91-120      | 181-280   | 169-208 | 10-17          | 381-800   | 801-1200   | 2.1-3.0   |
| Very poor (301-400) | 351-430     | 121-250     | 281-400   | 209-748*| 17-34          | 801-1600  | 1200-1800  | 3.1-3.5   |
| Severe (401-500)    | 430+        | 250+        | 400+      | 748+*   | 34+            | 1600+     | 1800+      | 3.5+      |