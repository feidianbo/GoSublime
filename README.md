GoSublime
=========

NOTICE
------

The project isn't dead, but there is a chance that I will become unresponsive for a little while take a brief hiatus to re-adjust to life.


Intro
-----

GoSublime is a Golang plugin collection for the text editor [SublimeText 2](http://www.sublimetext.com/2) providing code completion and other IDE-like features.

Features
--------

* code completion from [Gocode](https://github.com/nsf/gocode)
* context aware snippets via the code-completion popup to complement the existing SublimeText Go package.
* sublime build system(ctrl+b) allowing to run any command your shell will accept with some focus on the `go` command including support for cycling errors with F4/Shift+F4
* gotype support with errors highlighted in the editor view
* gofmt support for quickly reformatting your source to conform with the Go standards
* quick panel palette to:
	* jump errors (and jump back to where you were before (accross files))
	* list declarations in the current file
	* automtically add/remove package imports

MarGo
-----

Some features such as goto definition(currently only supports the current file) and auto-add/remove package imports are only available from MarGo. Additionally, in the future, most(likely all) features that depend on external commands (gofmt, etc.) will be removed and instead be implemented in MarGo.

An installation of MarGo will be attempted on Sublime Text startup if communication with MarGo fails.
If this doesn't work, or other errors are reported afterwards, please discuss it here: https://github.com/DisposaBoy/GoSublime/issues/44. You can install MarGo manually with command: `go get github.com/DisposaBoy/MarGo`

Other Dependencies
------------

If you haven't done so already, install [Gocode](https://github.com/nsf/gocode).
Gocode provides most of the code completion in GoSublime.

Demo
----

* http://vimeo.com/disposaboy/gosublime-demo2

![](https://github.com/DisposaBoy/GoSublime/raw/master/ss/2.png)
![](https://github.com/DisposaBoy/GoSublime/raw/master/ss/1.png)

Installation
------------

Recommended method
------------------

Sublime Package Control allows you to easily install or remove GoSublime(and many other ST2 packages) from within the editor. It offers automatically updating packages as well so you no longer need to keep track of changes in GoSublime.

1. Install Sublime Package Control (if you haven't done so already) from http://wbond.net/sublime_packages/package_control . Be sure to restart ST2 to complete the installation.

2. Bring up the command palette (default `ctrl+shift+p` or `cmd+shift+p`) and start typing `Package Control: Install Package` then press return or click on that option to activate it. You will be presented with a new Quick Panel with the list of available packages. Type `GoSublime` and press return or on its entry to install GoSublime. If there is no entry for GoSublime, you most likely already have it installed.

Alternative method
------------------

* Download GoSublime into your packages directory. You can access your package directory from within SublimeText by going to the menu `Preferences > Browse Packages...`. You can download a zipped archive or tarball on github via the `Downloads` button.

* Alternatively, you can simply clone this repo into your packages directory . (on Linux)

    $ cd ~/.config/sublime-text-2/Packages

    $ git clone git://github.com/DisposaBoy/GoSublime

Usage
-----

Please see USAGE.md for general usage and other tips for effective usage of GoSublime

Settings
--------

You can customize the behaviour of GoSublime by creating a settings file in your `User` package. This can be accessed from within SublimeText by going to the menu `Preferences > Browse Packages...`. Create a file named `GoSublime.sublime-settings` or alternatively copy the default settings file `Packages/GoSublime/GoSublime.sublime-settings` to your `User` package and edit it to your liking.

Note: Filenames are case-sensitive on some platforms(e.g. Linux) so the filename should be exactly `GoSublime.sublime-settings` with capitalization preserved.

Completion Markers
------------------

The following letters are used as suffix for entries in the completion list.

* ʂ - Snippets. These snippets are provided by GoSublime and should not be confused with SublimeText's snippets. Furthermore, they are context sensitive, therefore the snippets provided in the global scope will be different to those provided in function scope.

* ν - Variables

* ʈ - User-defined types, structs, maps, slices, etc.

* Ɩ - Constants

* ƒ - Functions

* ρ - Packages


