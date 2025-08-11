The technical details
=====================

.. _Github org: https://github.com/robot-rumble
.. _Robot Game: https://web.archive.org/web/20140101004828/http://robotgame.net/
.. _logic: https://github.com/robot-rumble/logic
.. _cli: https://github.com/robot-rumble/cli
.. _backend: https://github.com/robot-rumble/backend
.. _battle-viewer: https://github.com/robot-rumble/battle-viewer
.. _docs: https://github.com/robot-rumble/docs
.. _RustPython: https://github.com/RustPython/RustPython
.. _QuickJS: https://bellard.org/quickjs/
.. _Wasmer: https://wasmer.io
.. _WasmerJS: https://github.com/wasmerio/wasmer-js
.. _Play: https://www.playframework.com/documentation/2.8.x/Home
.. _Akka Streams: https://doc.akka.io/docs/akka/current/stream/index.html
.. _aws-lambda-rust-runtime: https://github.com/awslabs/aws-lambda-rust-runtime
.. _Elm: https://elm-lang.org
.. _fad: https://fsharpforfunandprofit.com/posts/ten-reasons-not-to-use-a-functional-programming-language

Robot Rumble is a complicated project made out of many interwoven components. My initial source of inspiration was the amazing `Robot Game`_ project, which was a robot competition site that revolved entirely around Python. This simplified its codebase, since all of the Python robots could be run inside of a Python chroot. But this also limited the scope of the project, and after it shut down, I was inspired to make my own version of this model.

Thus emerged the difficult infrastructural challenge at the root of RR: to create a remote code execution model that would 1) support multiple languages and 2) be able to run in multiple environments. Running battles in the **browser** is essential for creating a nice user experience, running on the **desktop** is necessary for IDE integration, and running on the **server** is necessary for feeding the site and giving the ELO rating system some credibility.

Our Remote Code Execution model
-------------------------------

The solution we settled for is to leverage webassembly, which was built for this very purpose. Under our system, we can support both types of languages:

 * We support **dynamic languages** by finding ways of compiling their interpreters down to wasm. This is easiest when they are written in an LLVM-compatible language, especially when they are written in Rust. For Python, we use the RustPython_ project. For Javascript, we use QuickJS_. This model is preferred because it allows running robots with no additional work on our part: once we compile the interpreters, we can instantly run any Python or Javascript program, anywhere.
 * We plan on supporting **compiled languages** by adding an additional step to the **server** and **desktop** environments that compiles the robot programs themselves to wasm. Compiling a dynamic language interpreter to wasm is doable; compiling *a compiler* to wasm is a lot less doable. As a result, we will never be able to support compiled languages in the browser editor. However, the benefit of wasm is that once we do run that initial compilation of the robot program, it instantly becomes runnable anywhere. If we compile on robot publish and store the resulting wasm code on our server, this will allow us to run compiled language robots in the browser also.

We achieve a consistent execution model for all three environments by using the fantastic Wasmer_ project. In the **browser**, we run wasm using WasmerJS_, and on the **desktop** and **server**, we run wasm using the Rust wasmer library.

Battle running logic
--------------------

But simply being able to run a robot program is not enough; instead, we need to combine two user programs together with a battle simulation algorithm. This algorithm needs to be able to maintain a complex battle state and update it over the course of a variable number of turns.

Rust was a perfect language for this task. We separated out our battle-running algorithm as a Rust crate with one key function:

.. code-block:: rust

    pub trait RobotRunner {
        async fn run(&mut self, input: ProgramInput) -> RunnerResult;
    }

    pub async fn run<TurnCb, R>(
        run_team1: Result<R, ProgramError>,
        run_team2: Result<R, ProgramError>,
        mut turn_cb: TurnCb,
        max_turn: usize,
    ) -> MainOutput
    where
        TurnCb: FnMut(&CallbackInput),
        R: RobotRunner,
    {
        ...
    }

This structure allows us to decouple our logic from our program runners, thus allowing a robot of any language to be simulated against a robot of any other language! Equally as important, this will also make it trivial to add new gamemodes down the road. All of the code that makes this happen is in the logic_ repo.

Running battles on the backend
------------------------------

Yet another challenge is how to scale the process of running battles on the server. This is unavoidable, since this is the only context that we have 100% control over, and thus the only context that we can use to generate ELO rating system.

Our solution uses a combination of AWS SQS and AWS Lambda. Our main server backend uses the Scala Play_ framework, and so we have easy access to `Akka Streams`_, which are perfect for a cloud queue like SQS. Every X minutes, our backend sends an SQS message for every battle that needs to be run. Each SQS entry is received by our lambda function, which uses Wasmer in the `aws-lambda-rust-runtime`_ to run the logic simulation. After the simulation procuces a result, this result is sent through a second SQS stream, through a second Akka stream, and the results are written to the database.


The Battle Viewer
-----------------

One last part of our stack is worth mentioning: the Elm_ battle-viewer code. Robot Rumble is a perfect example of a site that does *not* need to be a PWA. The majority of our pages do not need Javascript, and generating them server-side has drastically improved the simplicity of our codebase. This separation process has also allowed us to isolate the pages that *do* need to be dynamic, concretely, the editor and battle viewer.

For these dynamic pages, I chose my favorite tool: Elm_. The "no runtime errors" promise offered by statically typed functional programming languages is no fad_. This is particularly true in the case of a user interface, which constantly evolves in very radical ways. Coming from the JS framework ecosystem, I was genuinely amazed at how easily and quickly I could fundamentally change the structure of my dynamic Elm apps, since I was constantly aware of the exact ways in which the changes were breaking my programs.

All of our Elm code lives in battle-viewer_. The battle viewer itself is used in multiple different contexts (battle pages, editor page, rumblebot), and Webpack makes our complex build process possible.


Thus, the holy trinity: Rust, Scala, Elm
--------------------------------------------

If you've read this far, I'd love to hear your thoughts about our infrastructural choices. Shoot me an email: *antonoutkine at gmail dot com*.
