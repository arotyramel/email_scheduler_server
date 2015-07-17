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

On a Linux system execute by:

```
stdbuf -o 0 python main.py / 2>&1 | tee log.txt
```

Alternativly use the launcher file:

```
bash ./launcher.bash &
```
