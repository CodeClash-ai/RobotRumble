Publishing your robot
=====================

When you create a robot under your profile, it will initially be saved as a draft. In order for others to see your robot, and for the matchmaker to queue your robot for ranked battles, you need to **publish** it to a specific robot board by clicking the appropriate link on the page of the board. A **board** is a collection of robots and all of the battles that have occured between them. Boards can also optionally belong to a **season**, which is a period of fighting that lasts a specific amount of time.

The matchmaker queues battles for your robot both when it is published, and every X hours after that. The specific number of battles and hours depends on the board you are publishing to.


Deactivation
------------

Sometimes, your robot may be deactivated, which means that matchmaking is paused until you publish a new version of your robot. These conditions are:

1. **Erroring**: if your robot errors encounters an error that prevents any future execution, like a compile-time error, the match will terminate. If this happens |ErrorLimit| times in a row, your robot will be deactivated. The same rules applies to timing out: if your robot takes more than |Timeout| to execute |ErrorLimit| times in a row, it will be deactivated.
2. **Inactivity**: if a new version of your robot isn't published for |ActiveLimit|, it will be deactivated.
3. **Manual**: you can choose to manually deactivate your robot if you don't want it to participate in matchmaking.
