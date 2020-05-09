# CoolOrangeJuice
www.coolorangejuice.com <br>
"Orange Juice for health"

## Data Pipeline & Backend
Excel File must follow same format. <br>
From `load_data`
1. load specific sheet in an excel file -> `load_excel_sheet()`
2. load whole excel file -> `load_whole_excel()`
3. load all excel file from directory -> `flow_from_dir()` <br>
4. get result from HKJC if a dataframe has missing result -> `extract_missing_result()`
5. A. map HKJC result to data -> `map_result_to_day_data()`
6. B. map HKJC result to data -> `map_result_to_data()` <br>
    B. is the overall function, A is supportive, difference is A work from a single excel, B work from either single excel or directory

From `scraper`
1. `HKJCRaceResult` class -> initate a browser
    1. `load_race_source()` -> load a specific day and race
        1. `extract_race_tab()` -> extract race tab
        2. `extract_race_performance()` -> extract race performance
        3. `extract_race_result()` -> extract race result

## Tree
```
.
├── ETL
│   ├── fe_data_process.py
│   ├── geckodriver.log
│   ├── get_data.ipynb
│   ├── load_data.ipynb
│   ├── load_data.py
│   ├── result
│   │   ├── 04_29_2020_06_25_16.txt
│   │   ├── 05_01_2020_00_13_21.txt
│   │   ├── 05_01_2020_04_18_34.txt
│   │   ├── 05_01_2020_22_29_27.txt
│   │   └── 05_02_2020_00_16_32.txt
│   ├── scraper.py
│   └── tools.py
├── README.md
├── coding_kernel
├── model
│   ├── 4_22_2020_data.csv
│   ├── 5_2_2020_data.csv
│   ├── README.md
│   ├── geckodriver.log
│   ├── model_experiment_new.ipynb
│   ├── model_experiments_4_22_2020.ipynb
│   ├── model_experiments_5_2_2020.ipynb
│   ├── model_experiments_5_9_2020.ipynb
│   └── validatetor.py
└── recycle
    └── my_app.py
```
