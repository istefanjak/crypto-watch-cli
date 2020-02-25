# Simple Coinmarketcap API CLI portfolio

This is a simple implementation of the official [Coinmarketcap REST API](https://coinmarketcap.com/api/) in a python CLI application.

## Features
* Users can save cryptocurrency to their local portfolio file
* Users can track value of their holdings in BTC and USD
* Users can watch their portfolio value in "real time"*

\* The app is tested by using the basic free plan of the API, which allows 10000 requests per month. That would allow us to refresh the portfolio approx. every 4.5 minutes, if it ran 24/7. The default refresh rate is set to 5 minutes. If the user decides to use their paid plan, refresh wait time can be reduced.

## Installation and first time setup
 *Tested on Python 3.7*

Inside app root dir run:
```
pip install -r requirements.txt
```
For running the application use:
```
python app.py
```
If you run the bare application without any arguments like that, nothing will happen. We will discuss the list of subcommands and arguments in the **Commands section**.

For the first time setup, register on the official [Coinmarketcap REST API](https://coinmarketcap.com/api/) page and obtain the API key from the dashboard. Paste the key into the subcommand:
```
python app.py settoken <key>
```
If successful, a file named `token` inisde root dir is created. You can reuse the subcommand after setting the token if you wish to change the token in the future or there has been a problem with your token or `token` file. If you wish to delete the token, delete the `token` file manually.

## Commands
Use --help or -h optional arguments in every branch of subcommands inside CLI to show command line help.

```
app.py settoken token
```
* Positional argument `token`.
* Sets the coinmarketcap API token and saves it locally.

```
app.py insert (-n NAME | -s SYMBOL | -i ID) [--holdings HOLDINGS]
```
* Required options `-n` or `-s`  or `-i` (short versions) **exclusively**. Optional argument `--holdings` which defaults to 0.
* The `insert` subcommand searches for one valid cryptocurrency in the coinmarketcap database and if found adds it to the local portfolio with the number of holdings.

```
app.py remove id
```
* Positional argument `id`.
* Remove cryptocurrency from portfolio by their id  only. To obtain the id's in the portfolio run the `watch` command.

```
app.py purge
```
* Takes no arguments
* Remove all cryptocurrency from portfolio.

```
app.py watch
```
* Takes no arguments
* Watch the cryptocurrency from the portfolio and portfolio value. Note that Bitcoin is always being shown, regardless if it is in the portfolio or not. That being said, inserting a bitcoin entry with holdings 0 to the portfolio would make the entry irrelevant.

## Project files
`const.py` - contains constants like filenames of the portfolio and the token file and refresh rate for sending requests inside watch command.
