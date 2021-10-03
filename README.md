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
    │   ├── history.py      - query the history of the train. (for Shanghai and Beijing Railway EMUs.)
    │   ├── timetable.py    - timetable lookup module.
    │   ├── train_plan_graph.py - get the planning graph of the train no. using moerail.ml functionality.
    │   └── train_wifi12306.py - query train info from `com.wifi12306`
    ├── railroad_lib        - Some helper libraries taken from other projs
    │   ├── __init__.py
    │   ├── query12306.py   - By Lifan Zhang, for timetable function
    │   ├── query_wifi12306.py   - By AgFlore, for querying information from `com.wifi12306`
    │   ├── train_history.py - helper file for train no.
    │   └── TrainNoDB.py    - a searchable db of train numbers. Saved for future functionalities.
    └── requirements.txt    - python packages required 

## Contributing

All contributions are welcome.

## Licence

GPL V3

## Author and Acknowledgements

Main function made by waymao, with the help from lfz.

Huge thanks to the developer of the python telegram bot library.
