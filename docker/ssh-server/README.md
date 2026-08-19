# Real SSH lab source

This optional container runs a real OpenSSH daemon for controlled local testing.
It is not a production SSH server. The default credentials are intentionally lab-only and should be changed via `.env`.

Start it with the `real-ssh` profile through `./lab.sh start --mode hybrid --real-ssh`.
