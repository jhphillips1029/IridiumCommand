# Development Notes

## Overview
This section will provide an overview and details of in-work or planned improvements to Iridium Command Center.

# Table of Contents

* [Overview](#overview)
* [Rewrite README](#rewrite-readme)
* [Documentation](#documentation)
* [Executables](#executables)
* [Restructured File Heirarchy](#restructured-file-heirarchy)
* [Integration With LoRa](#integration-with-lora)
* [Integration With Ground Station](#integration-with-ground-station)

## Rewrite README
**Overview:**

README.md can be rewritten to better convey purpose, installation, and new user introduction.

* About
    * => Overview
    * Provide the who, what, when, where, why, and how
* Installing
    * Break into subsections documenting different methods of installing
        * git, .zip, etc
    * Include images
    * (w/ [Executables](#executables)) How to use executables
* Running
    * => Quick Start Guide
    * Manual build
        * What to do to get started
    * (w/ [Executables](#executables)) Release executables
        * What to do with the executable

**Progress:**

* Included image of "home screen"
  * Provides some "what"
  
## Documentation
**Overview:**

Provide in-depth documentation on what the fuck is going on.

* How to use
    * More in-depth than quick-start guide
    * How to customize (making your own widgets, colors, logos, etc)
* How to contribute
    * Preferred naming conventions, etc

**Progress:**

None
    
## Executables
**Overview:**

[PyInstaller](https://pyinstaller.org/en/stable/) can be used to create executables for easy use.

* Setup .spec file for generating one-file executable
* Can one .spec create executables for *nix and Windows?

**Progress:**

None

## Restructured File Heirarchy
**Overview:**

File heirarchy should be restructured to keep widgets separated (ie, keep all files associated with Overview separated
from all files associated with Tracker)

* Group widget files into folders
* Rewrite dynamic imports

**Progress:**

* Logo image files moved to 'images' folder

## Integration With LoRa
**Overview:**

Integrate the Larson Brandstetter's LoRa GUI as a widget.

**Progress:**

Unknown

## Integration With Ground Station
**Overview:**

Integrate the Matthew Clutter's Ground Station tracking software GUI as a widget.

**Progress:**

None
