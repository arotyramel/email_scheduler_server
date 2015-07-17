# email_scheduler_server
Command line server programm for scheduling emails.

##Current functionality:
	* Send mails at a specific date/time
	* Send mails with a specific interval until a response with a keyword is found
	* Feedback of mail jobs
	* Feedback on errors
	* All temporary data is stored once every minute in case there is a powerloss.

	* Shopping function: Accumulate items during the week.
	* All accumulated items are sent and reset once a week. 


##Installation

Install some dependencies:

```
pip install python-dateutil
```

or

```
sudo apt-get install python-dateutil
```


##Execution

On a Linux system run the server with the launcher file in main directory:

```
bash ./launcher.bash &
```

## Autostart
Add this line to your "/etc/rc.local", replacing the path with the correct path to your the launcher.

```
sudo ${USER} -c "/home/pi/email_scheduler_server/launcher.bash" &
```
