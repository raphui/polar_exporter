# polar_extractor
Export data from polar personal trainer to polar flow

## Installation
pip3 install requests

pip3 install docopt

pip3 install beautifulsoup4

## Usage
```
  polar_export.py LOGIN PASSWORD START_DATE END_DATE [--custom=<filepath>]
  
  polar_export.py (-h | --help)

Arguments:

  LOGIN         Polar personal trainer login
  
  PASSWORD      Polar personal trainer password
  
  START_DATE    Start date: dd.MM.YYYY
  
  END_DATE      End date: dd.MM.YYYY

Options:

  -h --help     Show this screen.
  
  -c --custom=<filepath>   List for sports that is in Polar Personal Trainer but not in Polar Flow sports list.
```
