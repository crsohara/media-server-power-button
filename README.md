# Media server power button

## Requirements
- RPI GPIO: `sudo apt-get install rpi.gpio`
- python3
- python dotenv: `pip3 install python-dotenv`

## Run on boot:
Edit crontab `crontab -e` and add the following line:
```
@reboot python3 /path/to/repo/button.py &
```
