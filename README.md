# TwistAR: Flexible Body, Flexible Life!

*An exergame created by Girish Krishnan and Yang-Jie Qin*

__Our intended target users are people who have long, monotonous work hours involving little mobility.__ Some examples of our intended users are desk receptionists who need to sit at a desk all day, and security guards or watchmen standing in front of a gate.

__Here's the main use case or problem we aim to address:__

_People who need to stay immobile for long hours working at a desk find it difficult to get sufficient exercise, due to their busy schedule and long work hours. This can lead to stress, stiffness, and even muscle cramps resulting from a lack of exercise. Our task is to make exercise fun and enjoyable through an accessible mobile application._

Our product could potentially be used by a wide audience, and can encourage physically inactive people to exercise more. 

__Why is this problem worth addressing?__

Although we are in a post-COVID era, a lot of meetings and tasks are still carried out online. Most classes have an online format for assignment submission, and a lot of students spend hours in front of a screen to complete assignments or study for exams. We came across the issue of being idle at a desk when observing the receptionists and community service officers at Geisel library, who stay planted in one spot for a long time.

Being idle for too long can have health consequences, such as muscle cramps, stiffness, lack of stamina, and mental stress from being overworked. To avoid these consequences, why not invest in a fun, addictive game that keeps your muscles in tune?

__How is our solution addressing the needs of the user?__

In our fitness game, we challenge the player to achieve specific postures by stretching their body. The more postures they complete, the higher their score and the more levels they complete. This game will be available as an app, so the game is easily accessible and the players need nothing but a laptop/other device with a webcam. However, we also have an add-on controller for the game, where we use the ESP 32. The controller for the game is completely optional, but it can be a useful add-on to the smart wearable we created in Lab 7.

The fitness challenges in this game encourage the user to stretch themselves to alleviate stress. The game is highly flexible, and the user can spend as much time as they want on it (so it's compatible with breaks during work hours). Our game clearly alleviates the monotony that arises from being idle at a desk for a long time.

__Competitors?__

Our potential competitors are other fitness 'exergames' that are available on the market. These fitness 'exergames' typically use a gaming station such as the Xbox or PlayStation. Unfortunately, gaming stations such as the Xbox and PlayStation are expensive and workers with low income may not invest in them. Furthermore, gaming stations require a decent amount of bulky hardware, making them impossible to use during breaks in an office.

Our solution, on the other hand, is flexible because it can be used in two different ways:

* As a free version, using only the software (which is all open-source)
* As a paid version, which involves the controller for the game

__Our Design Process__

Answering the questions above helped us come up with a solid design that would fulfill the problem we'd like to solve. To implement pose detection, we used the __mediapipe__ library (created by Google), which uses machine learning over a large trained dataset to detect poses in images and live video. The pose detection algorithm in mediapipe finds 33 "landmark" positions in the person's body (such as hands, feet, etc.), and gives the coordinates of these landmarks. Thus, these coordinates helped us determine whether the player was at the correct position or not.

Once we implemented pose detection in live video, we moved on to creating a 4x4 array of colored circles on the screen, where the player would have to place their hands and feet to achieve specific postures. We decided to implement this with the left hand, right hand, left leg, and right leg, to make the game fun. During every level, the player must position their hands and/or feet at a different position. As players successfully achieve a specific posture, they move on to higher levels.

We designed the game to be like this so that it can be played flexibly for any length of time to accommodate different people's work and break schedules. We also wanted the game to be accessible, so we made a free-version using only software, as well as a paid version involving the controller (hardware).

The controller's design is as follows:

* There are 4 LEDs, and one of them lights up indicating the most recent color that has been randomly selected by the computer.
* The OLED display shows the current level and the most recent color and hand/leg combination that needs to be achieved next.
* If you flip the OLED display sideways (we've used this mechanism before in the controller for Space Invaders), then the OLED display changes to show all the 4 limbs along with the colors on which each limb needs to be placed.
* The controller is connected via Bluetooth.


__Testing the accuracy and reliability of the game__

It's always important to ensure that the game can correctly detect whether the player has correctly positioned their hands and legs to achieve each position. To assess this performance, we took snapshots of the game where the player's position is plotted to show how each hand/leg position correctly matches the corresponding color. This is an example of a snapshot when level 5 was achieved and when level 6 was about to begin:

![](images/plot1_showinglevels.png)

Note that the abbreviations LH, RH, LL, RL stand for left hand, right hand, left leg, and right leg, respectively. The controller for the game is shown on the left-hand side, showing the most recent color (indicated by LED) and the current status of the game (shown on OLED). We can clearly see that the pose detection is accurate. 

Here is a plot showing the game after level 6 is correctly achieved:

![](images/plot2_level6completed.png)

Clearly, each limb is placed alongside the correct color, and the positions are reasonably close enough to be considered a "correct" posture by the computer. 

Further plots such as these helped us debug the program and check for any potential errors in the game's ability to detect correct posture.