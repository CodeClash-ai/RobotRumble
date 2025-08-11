Develop robots locally with rumblebot
=====================================

.. _Wasmer: https://wasmer.io

Are you in love with your 10GB IDE? Are you a vimaholic that is annoyed by the millisecond delay caused by entering code in your browser? Rumblebot is here for you. `Download it on Github.`__

__ https://github.com/robot-rumble/cli/releases

**Features**

 1. Easily run robot programs stored on your filesystem, which makes it possible to use a custom IDE.
 2. View battle results in both a web GUI (like on the site), or directly in your terminal.
 3. Easily create and update robots from the command line.

**Installation**

 1. Download the appropriate release from the Github releases page.
 2. Unzip the folder somewhere in your filesystem.
 3. Open a terminal and navigate to the folder. If you've never used a terminal before, you can read a quick primer here__ (it's way easier than it seems!) In this case, you will want to run ``cd [FOLDER_PATH]``.
 4. On windows, you can go ahead and run the program with ``./rumblebot.exe``. On Macos/Linux, you first need to make the ``rumblebot`` file runnable by executing:

    .. code-block:: bash

        chmod +x ./rumblebot

    Then you can run it with ``./rumblebot``.

**Please note**: Just because your robots live in the filesystem does not mean that you can import external dependencies. Support for third-party packages is on the roadmap, but implementing it is a very nuanced challenge. If you really, really need a library, your best bet is to minify it and just include it at the top of your program.

**Security**: Every robot in a Robot Rumble battle is run within a fully sandboxed Webassembly runtime. In the browser, we use the V8 engine, and on the desktop/server, we use Wasmer_. This means that it is impossible for a robot's code to access any part of your system, aside from a couple modules necessary for reading time and generating entropy.

__ https://lifehacker.com/a-command-line-primer-for-beginners-5633909

