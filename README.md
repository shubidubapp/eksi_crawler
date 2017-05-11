# Ekşi_Crawler

usage: eksi_crawler.py [-h] [-st START] [-sp STOP] [-o OUTPUT] [-tc THREAD_COUNT] [-c CONTINUE_TO_FILE]

optional arguments:
  * -h, --help  
      show this help message and exit
      
  * -st START, --start START  
      Starting entry number for crawler. (included) Default:1 
      
  * -sp STOP, --stop STOP 
      Stopping entry number for crawler. (not included)Default: 1 000 000 000 
      
  * -o OUTPUT, --output OUTPUT  
      Output file name. Default: eksi_crawler_out.txt \n
  * -tc THREAD_COUNT, --thread-count \n
      THREAD_COUNT Limit the amount of threads created. Default: 4 \n
  * -c CONTINUE_TO_FILE, --continue-to-file CONTINUE_TO_FILE  \n
      Continue with the stated file from last index outputs to that file. \n
                        

*Gotta fix those errors popping up when you press Ctrl-C*
