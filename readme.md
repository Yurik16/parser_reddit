# parser_reddit

"parser_reddit" is a Python script program that collects data from https://www.reddit.com <br />
Top 100 posts of the month.

## Installation
Before install you must have:

<ul>
    <li> Python 3.7+
    <li> Git bash
    <li> Selenium
    <li> last update for `Chromedriver` https://chromedriver.chromium.org/home
</ul>

Clone repository - git clone https://github.com/Yurik16/parser_reddit.git <br />
Before run parser.py move to working folder and install all packages from requirements.txt. Execute: <br />
<ul>  
    <li> virtualenv venv
    <li> source venv/bin/activate
    <li> pip install -r /path/to/requirements.txt
</ul>

## Usage

Executive file: parser.py <br />

Using the terminal you can add arguments and change number of parsing posts (python3 parser.py --count), file path for saving result *.txt
file (python3 parser.py --filepath)

## returns

Returns reddit-*.txt file with top 100 posts. Each line in that file contains: \
UNIQUE_ID; post URL; username; user karma; user cake day; post karma; comment karma; post date; number of comments;
number of votes; post category

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)