# Iridium Command Center

## Table of Contents
* [Google Account Information](#google-account-information)
* [Installing the Program](#installing-the-program)
* [Running the Program](#running-the-program)
* [Google API Credentials](#google-api-credentials)
* [Adding Testing Users](#adding-testing-users)

### Google Account Information
See the BOREALIS Teams page or ask Randy.

### Installing the Program
If you have git installed, simply use the command `git clone https://github.com/jhphillips1029/IridiumCommand`.

If you do not have git installed, follow the directions below
1. Navigate to the top of https://github.com/jhphillips1029/IridiumCommand
2. Click the green 'Code' button and select 'Download ZIP'.
3. Extract the file to an appropriate location.

### Running the Program
The program can be run using the `python ICC.py` command.

1. Select 'Tap To Select Profile' along the bottom of the screen to create a profile.
2. Select a command from the orange radio buttons in the center column.
3. Select 'Send Command' and confirm the command to send out the Iridium command.

Notes:</br>
* If you are not connected to the internet, the program will crash.
* On the first run of the program, you will need to edit the current profile or create a new one to include an actual IMEI number.
* When you generate new credentials (for whatever reason), you MUST delete the old token.pickle.
* The program will not begin if the user associated with the credentials has not been added as a testing user.

### Google API Credentials
1. Navigate to https://console.cloud.google.com/home/.
2. Using the dropdown in the top bar (near the center), select 'Iridium Emailer'.
3. Using the menu on the left-hand side of the top bar, hover over 'APIs and Services' and select 'Credentials'.
4. Scroll to OAuth 2.0 Client IDs to find 'Iridium Command'. Scroll to the right on this option and select the download. Save the .json file as 'credentials.json'.
5. Run ICC.py and sign in through the OAuth screen. You should be set to go now.

### Adding Testing Users
1. Navigate to https://console.cloud.google.com/home/.
2. Using the dropdown in the top bar (near the center), select 'Iridium Emailer'.
3. Using the menu on the left-hand side of the top bar, hover over 'APIs and Services' and select 'OAuth consent screen'.
4. Select the 'Edit App' option next the Iridium Command name.
5. The first page is 'OAuth consent screen'. Scroll to the bottom and select 'SAVE AND CONTINUE'.
6. The second page is 'Scopes'. Scroll to the bottom and select 'SAVE AND CONTINUE'.
7. The third page is 'Test users'. Click '+ ADD USERS'.
8. Type in the new users' email addresses and click 'ADD'.
9. Click 'SAVE AND CONTINUE' and then 'BACK TO DASHBOARD'.
