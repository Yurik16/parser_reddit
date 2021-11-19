# parser_reddit

"parser_reddit" is a Python script program that collects data from https://www.reddit.com \
Top 100 posts of the month.

## Installation

Just сlone repository - git clone https://github.com/Yurik16/parser_reddit.git \
Before run parser.py install all packages from requirements.txt -> pip install -r /path/to/requirements.txt

## Usage

Executive file: parser.py \
Default NUM_OF_PARSING_POSTS - 100 (line 26 at parser.py default=100)\
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