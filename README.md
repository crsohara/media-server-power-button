# Media server power button

Setup to run on boot:
```
sudo chmod +x button.py
crontab -e
```
Add the following line:
```
@reboot python3 /path/to/repo/button.py &
```
