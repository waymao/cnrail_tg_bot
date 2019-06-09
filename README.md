# China Railway info query bot

A bot to look up useful info about the china national railway.

## Installing

After downloading the project, please run:

    pip install -r requirements.txt

## Running

    python3 bot.py

## Files

    ├── README.md           - this file
    ├── bot.py              - Main handler for the bot
    ├── bot_config.py       - Configurations for the bot.
    ├── bot_logging.py      - Logging settings.
    ├── commands            - Command folder. for all commands and other callback
    │   ├── __init__.py     - imports py files and adds handlers to the list.
    │   ├── basics.py       - Basic welcome module.
    │   └── timetable.py    - timetable lookup module.
    ├── railroad_lib        - Some helper librarys taken from other projs
    │   ├── __init__.py
    │   └── query12306.py   - By Lifan Zhang, for timetable function
    └── requirements.txt    - 

## Contributing

All contributions are welcome.

## Licence

GPL V3

## Author and Acknowledgements

Main function made by waymao, with the help from lfz.

Huge thanks to the developer of the python telegram bot library.
