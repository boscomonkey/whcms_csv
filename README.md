# WHMCS CSV importer

TL;DR quick & dirty Python script to import new clients from a CSV into WHMCS.

## Backstory

A friend was planning to import several hundred new clients into WHMCS by hand-entering each client through the New Client page. I figured I'd help out by automating the process with a Selenium script written in Python.

The script iterates through the CSV one row at a time, enters the new client info in that row into WHMCS's New Client page, and clicks Submit. Then rinse and repeat until all the rows are processed.

## Technical Part

The script currently uses Python 2.7 and Firefox. Why 2.7? Because that's the default version installed on Mac High Sierra. Why Firefox? Because I was familiar with its console interface from my last job. The code should work on Chrome, however.

### Set up

1. Clone this repo.
1. Use _virtualenv_ to create a _venv_ directory somewhere. I recommend the project root.
   ```
   $ cd whmcs_csv
   $ virtualenv venv
   ```
1. Install the packages in _requirements.txt_.
   ```
   $ pip install -r requirements.txt
   ```
1. Download Mozilla's [geckodriver](https://github.com/mozilla/geckodriver/releases) and put it on your path somewhere (e.g., `/usr/local/bin`, `~/bin`). This is the software that Selenium talks to that controls Firefox.

### CSV

The global hash `CSV_HEADER` in [whmcs_csv_importer.py](https://github.com/boscomonkey/whmcs_csv/blob/master/whmcs_csv_importer.py) maps the header values in the CSV file to arguments for the _WhmcsCsvImporter_ instance method `enter_new_client_info`.

So, if you don't have the custom fields specified in `CSV_HEADER`, you'll need to comment those fields out, as well as comment out the corresponding arguments & code in `enter_new_client_info`.

### Run It

You can run the CSV importer from the command line. Don't forget to load the virtual environment first:
```
$ source venv/bin/activate
$ python whmcs_csv_importer.py \
    WHCMS_URL \
    USERNAME \
    PASSWORD \
    CSV_FILENAME \
    [SUBMIT]
```
Where:

* WHCMS_URL - URL of your WHCMS admin login page
* USERNAME -  Username of your admin user who can create new clients
* PASSWORD -  Password of your admin user who can create new clients
* CSV_FILENAME - file name of your CSV
* [Optional] SUBMIT - if the argument is the literal "SUBMIT", the new clients will be submitted; otherwise, it's a dry run.

## Fun Fact

I'm using the [xkcd password generator](https://github.com/redacted/XKCD-password-generator) package to generate passwords.
