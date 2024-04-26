# MLP to Portfolio Performance Converter

A Python script to convert MLP bank data to a CSV file understood by [Portfolio Performance](https://github.com/buchen/portfolio).

## Input

A CSV file generated by exporting transaction data from an MLP bank account.

## Output

A CSV file that can be imported by Portfolio Performance.

## Requirements

Python 3.2 or higher

## Instructions

1. Install Python 3.2 or higher.
2. Download the current release and extract it to a folder `C:\User\your_name\mlp-to-portfolioperformance-converter`
3. Open the transactions of the clearing account in MLP Financepilot Banking. Set the desired time period. Export the data as CSV (top right, the icon above "Current") and save the file as `C:\User\your_name\Downloads\Umsaetze.csv`.
4. Press Windows key + X.
5. Select Windows PowerShell
5. Navigate to `cd C:\User\your_name\mlp-to-portfolioperformance-converter`.
6. Run the script with `python mlp_to_portfolio_performance_converter.py ~\Downloads\Umsaetze.csv`.
7. Check the output for errors. If everything went smoothly, there should now be a file `~\Downloads\Umsaetze_converted` that can be imported into Portfolio Performance.

## Contribution

Fork the repository and clone it your local drive. 
Open the folder in an IDE of your choice. 
I recommend PyCharm or VSCode.
This repository has unit tests `test_*`. Run these to ensure that you don't break existing features.
Idealy add tests that are testing your new feature.