# S.P.I.N.S.

Scape Player Intoxication Notification System

This program reads alcohol sensor data from an Arduino over a serial port. It calculates the estimated BAC and logs it
continuously. Every few seconds it writes the BAC value and a true/false status to a Google Sheet. It is designed to
work with a RuneLite plugin that reads the values from the Google Sheet. The program runs in a Python virtual
environment and updates the sheet automatically.

How to install:

clone the repository
`git clone git@github.com:abristow3/S.P.I.N.S..git`
`cd S.P.I.N.S.`

run the install script
`./install.sh`

the script will create a virtual environment install required packages and launch the bac monitor python script
