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



On a Linux system run by:
stdbuf -o 0 python main.py / 2>&1 | tee log.txt