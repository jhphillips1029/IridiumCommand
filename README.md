# Iridium Command Center

## Table of Contents
* [About](#about)
* [Installing](#installing)
* [Running](#running)
* [Modifying](#modifying)

### About

The Iridium Command Center (ICC) was designed to optimize the process of sending commands to BOREALIS weather balloon payloads after our long-time flight director retired.

Previously, the commands were hand-crafted and emailed by the flight director during flight. Now, the commands can be sent through a customizable GUI with aliases for different commands, hopefully reducing the potential for sending erroneous commands.

Additionally, several more functions have been added, and the program made modular, so it can be used by any of the several university ballooning groups around the US.

### Installing

To begin, you will need to install [Anaconda](https://docs.anaconda.com/anaconda/install/index.html). This is because the conda package manager pulls in some required C files that pip does not.

Download this repo using the 'CODE' button above, [this link](https://codeload.github.com/jhphillips1029/IridiumCommand/zip/refs/heads/master), or by creating a new directory and running the command `git clone https://github.com/jhphillips1029/IridiumCommand`. If you downloaded a .zip file, unzip it to an appropriate location.

Open a terminal window and navigate to the directory containing the code. Run the command `conda install -c conda-forge --file requirements.txt`. This will install the necessary dependencies to run the code.

Finally, you will need to generate credentials for the email portion of the controls. To do so, please follow the directions in <i>[Generating Google Credentials](#generating-google-credentials)</i> (modified from [these](https://developers.google.com/workspace/guides/create-credentials#desktop) instructions).


### Running

Open a terminal window and navigate to directory containing the code.

In Windows, run the command `py main.py`.<br>
In most other real operating systems, run the command `python main.py`.

This will bring up the ICC. It comes pre-installed with three main functions, each accessible under its own tab on the left-hand side of the GUI. These three functions are the base functions necessary for sending Iridium commands.

### Modifying

ICC is designed to be modular. As a result, you can create your own widgets to add to the GUI. An example widget named 'Demo' can be found in the widgets folder. To load this into the GUI, comment it out in widgets/.ignore.

### Generating Google Credentials

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Next to <b>Google Cloud Platform</b>, click the Down arrow and create a new project.
    * Name the project "Iridium Command Center"
    * Click <b>Create</b>.
    * Next to <b>Google Cloud Platform</b>, click the Down arrow and select "Iridium Command Center".
3. At the top-left corner, click Menu.
4. Click <b>APIs & Services > Credentials</b>. The credential page for your project appears.
5. Click <b>Configure Consent Screen</b>. The "OAuth consent screen" screen appears.
6. Select <b>External</b>.
7. Click <b>Create</b>. A second "OAuth consent screen" screen appears.
8. Fill out the form:
    * Enter "Iridium Command Center" in the <b>App name</b> field.
    * Enter your email address in the <b>User support email</b> field.
    * Enter your email address in the <b>Developer contact information</b> field. (You can't get my email that easily!)
9. Click <b>Save and Continue</b>. The "Scopes" page appears.
10. Click <b>Add or Remove Scopes</b>. The "Update selected scopes" page appears.
13. Click <b>Save and Continue</b>. The "Test users" page appears.
14. Click <b>Add Users</b>. The "Add users" page appears.
15. Type in your email address and click <b>Add</b>.
16. Click <b>Save and Continue</b>. The "Summary" page appears.
17. Click <b>Back To Dashboard</b>.
18. At the top-left corner, click Menu.
19. Click <b>APIs & Services > Dashboard</b>. The dashboard page for your project appears.
20. Click <b>Enable APIs and Services</b>. The "API Library" page appears.
21. Search for "Gmail API" and select it. The "Gmail API" page appears.
22. Click <b>Enable</b>. You will be returned to the dashboard page.
23. At the top-left corner, click Menu.
24. Click <b>APIs & Services > Credentials</b>. The credentials page for your project appears.
25. Click <b>Create Credentials > Help me choose</b>. The "Create credentials" page appears.
26. Select "Gmail API" from the drop-down and click <b>User data</b>. Then click <b>Next</b>.
27. Click <b>Add or Remove Scopes</b>. The "Update selected scopes" page appears.
28. Seach for "ht<span>tps://</span>ma<span>il.go</span>ogle.c<span>om/</span>" and tick the box to the left of it.
29. Click <b>Update</b>. This returns you to the previous screen.
30. Click <b>Save and Continue</b>.
31. Select "Desktop app" from the drop down. You may name the machine as you please.
32. Click <b>Create</b>.
33. Click <b>Download</b>. Save to the same directory as ma<span>in.p</span>y. Save the file as "credentials.json". Do <strong>NOT</strong> forget to save as "credentials.json".
34. Click <b>Done</b>.
