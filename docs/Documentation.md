# Iridium Command Center
##### Joshua H. Phillips

-----

## Table of Contents
* [Table of Contents](#table-of-contents)
* [Introduction](#introduction)
  * [Background](#background)
  * [Project Goal](#project-goal)
  * [Project Description](#project-description)
* [Primary App](#primary-app)
* [Completed Widgets](#completed-widgets)
  * [Overview](#overview)
  * [Tracker](#tracker)
  * [Profiles](#profiles)
  * [Adv Profiles](#adv-profiles)
  * [Filling](#filling)
* [Unfinished Widgets](#unfinished-widgets)
  * [Cadastral](#cadastral)
  * [Ground Station](#ground-station)
  * [Filling With Weather Station](#filling-with-weather-station)
  * [Network](#network)
  * [Updates](#updates)
  * [Widgets](#widgets)

-----

## Introduction

The Iridium Command Center (ICC) provides a platform for sending commands to scientific equipment as well as the development of future code to facillitate such operations.

### Background

The Balloon Outreach, Research, Exploration, And Landscape Imaging System (BOREALIS) lab, as a part of the Montana State University (MSU) division of the Montana Space Grant Consortium (MSGC), uses the Iridium satellite network to send commands from the ground to payloads on high altitude balloons (HABs). Sending a command through the Iridium network involves first constructing an email in a particular format, sending the email to be processed by the Iridium servers, transmitted to the Iridium satellites, and finally transmitting to the Iridium modem on the HAB payload string. These commands define what state the Iridium data pins are set to. This command remains the same until the next command is sent. Previous to Summer 2021, BOREALIS flight directors would manually construct and send the email using only the pin states to differentiate commands.

### Project Goal

The primary goal of the ICC is simplifying the process of sending a command to the HAB payloads to only a few clicks/touches. This entails aliasing the pin states of the Iridium, automating the construction and sending of Iridium command emails, and checking confirmation emails.

The secondary goal of the ICC is to provide a base for the development of future BOREALIS GUIs. This entails creating a modular program and creating standards for modular widgets.

### Project Description

The ICC uses three primary widgets ([Overview](#overview), [Tracker](#tracker), and [Profiles](#profiles)) in a main application to simplify the process of sending commands to HAB payloads and also provide a base for development of future GUIs.

## Primary App

The main application consists of two sections divided graphically in the application. The upper portion of the application includes (from left to right, top to bottom) a log window, application name, date and system time, and MSGC logo. The log window shows log output from the main application and all running widgets, regardless of active widget.

The lower portion of the application includes the widget selector and widget socket. The widget selector displays all the loaded widgets and includes markers to indicate which widget is currently active. The widget socket is the area reserved for individual widgets and takes care of widget requests such as logging and alert levels. The main application is responsible for determining which widget is active and should be displayed while the rest are hidden as well as importing and initializing the widgets. If a non-primary widget (something other than [Overview](#overview), [Tracker](#tracker), and [Profiles](#profiles)) fails to load, it will be ignored and will not affect other widgets.

Additionally, the main application includes a splash screen to show the program is loading on startup using the logo from the upper portion of the main application as a background, the main application records all log messages to a file and manages the number of log files, and the main application takes care of closing and resizing.

## Completed Widgets

[Brief intro paragraph]

All widgets inherit the Widget class imported from Widget.py. This abstract class provides functions for resizing, showing, hiding, tracking components, and setting command profiles. The resizing takes care of both size and font effects as well as any specific effects of an individual widget.

### Overview

The Overview widget is responsible for sending commands. From left to right, the graphical components are the alert states, the confirmation dialogue, the pin state/command alias pin out and 'Send Command' button, and the aliased command selector.

The alerts do not currently serve a purpose beyond complimenting the graphical theme of the application. When an alert state is chosen, it is logged, all colors are overridden to the alert color chosen, and a ring begins to blink around the widget socket in the selected color. The alert remains active until the user selects the 'Cancel Alert' button.

The pin state/command alias pin out serves to remind the user of the profile chosen, the Iridium modem selected (as indicated by the IMEI number), and the exact pin states that go with the aliased commands. Initially, fields will be marked as 'Not set' until a profile is chosen or created in [Profiles](#profiles) or [Adv Profiles](#adv-profiles). When a profile is loaded, the pin out and command selector will be updated.

When the 'Send Command' button is selected, it will bring up a dialogue box asking for confirmation that the command is correct. If the command is cancelled at this point, it will be logged, and no further action will be taken. If accepted, an email will automatically be constructed in the proper format and sent. The 'Send Command' button will be locked out until confirmation is received.

When confirmation has been received that the command has been received by the Iridium servers, the confirmation dialogue will be updated with the confirmation email statistics, and the 'Previous Command' section will be updated with the command sent.

The command selector keeps track of and indicates as to which command has been selected. When a profile is selected, the pin states on each of the selectors will be updated to the associated alias.

### Tracker

The tracker widget is responsible for displaying the location of the balloon and statistics about the location of balloon. This is accomplished by a map (with controls), a display of statistics, and a plot of the balloons elevation. The data for tracking the balloon is obtained from [this BOREALIS site](https://borealis.rci.montana.edu/tracking).

Because conventional mapping libraries in Python do not play well with Tkinter, a custom mapping library had to be written using matplotlib and updateing image frames in Tkinter. This shows the location of the balloon on a 2D projection.

The statistics included in the statistics display include decimal values for latitude and longitude; altitude in meters and feet as well as altitude above ground level in meters; the vertical and ground velocities in m/s; and the percent of the atmosphere by mass below the balloon payloads.

The altitude plot uses many of the same methods of rendering a plotted image as the map does.

### Profiles

The profiles widget is split into two halves graphically. The left half displays the currently selected command profile with the option of loading a new profile. The right half includes interactive text boxes to edit and existing profile or create a new one with options to save as a new profile or overwrite the existing one.

Command profiles are saved as JSON files including the name of the profile, the IMEI of the Iridium modem used, and the aliases of the pin states used for commands.

### Adv Profiles

The advanced profiles widget is structured similarly to the profiles widget with the exception that it shows the entire contents of the JSON file and allows the user to edit the entire contents of the JSON file. This is useful if other widgets require access to flight-specific variables, those variables can be stored as a part of the flight command profile.

### Filling

The filling widget is responsible for calculating the pressure differential as seen by the helium tanks for filling helium balloons. Some numbers remain constant, such as the volume of the helium tanks, the pressure of the helium tanks, and the purity of the helium; whereas, others can change, such as the elevation of the launch site, and the ambient temperature, pressure, and humidity. The constant variables could be stored in the flight command profile and loaded when the profile is loaded.

Additionally, the ambient conditions and pressure altitude may be obtained from a serial connection. The BOREALIS Weather Station Rev 2 uses a BME680 environmental sensor to collect ambient pressure, temperature, and humidity and relays that data as well as the pressure altitude through serial. Serial communication must be JSON format.

## Unfinished Widgets

These widgets are all in some stage of completion, listed in order of closeness to completion.

### Cadastral

This widget is responsible for accessing the Montana State Library's cadastral database to determine property ownership. This widget was implemented into the ICC during the last flight of Summer 2021 but experienced severe lag due to the large number of properties present in individual counties and accessing the cadastral database live over the internet. This widget requires optimization to function properly.

### Ground Station

Matthew Clutter's work on the [ground station software](https://github.com/mathias314/Ground-Station-Tracker) used PyQT as the means of creating a GUI, so all that remains to do is recreate the GUI as a Tkinter interface using the tools provided by the Widget class. This widget requires integration with a (nearly) completed project to function properly.

### Network

The network widget would allow multiple users to share data over the local network or the internet if devices were set up correctly. Currently, this widget is only able to connect over the local network and automatically updates alert state and command profile as determined by the master device in the network. This widget requires a refined purpose to function properly.

### Updates

This widget would manage updates to the main application alerting the user when there is a new version available and allow the user to manually or automatically update the system. This widget has only been conceptualized.

### Widgets

Similar to the updates widget, this widget would manage updates for individual widgets. Additionally, it is envisioned to allow for multiple widget sources and reload widgets without closing and reopening the main application. This widget would require restructuring of the file heirarchy for the widgets folder. This widget has only been conceptualized.

