Flappy Bird - Java (Swing)
A simple, lightweight desktop version of the classic Flappy Bird game, built from scratch using Java Swing and AWT. Guide your bird through an endless obstacle course of pipes and aim for the highest score!

Features
Smooth Physics:-
Responsive bird movement and gravity simulation.

Infinite Gameplay:- 
Continuous, random pipe generation.

Collision Detection:-
Accurate hitboxes for the bird, pipes, and ground.

Score Tracking:-
Real-time score updates as you successfully pass through pipes.

Custom Graphics:- 
Background, bird, and pipe sprite rendering.

Intuitive Controls:- 
Simple keyboard inputs.

Project Structure:-
Flappy-Bird/
├── App.java              # Main application entry point & window setup
├── FlappyBird.java       # Core game logic, rendering, and physics
├── flappybird.png        # Bird sprite
├── flappybirdbg.png      # Background image
├── toppipe.png           # Top pipe sprite
├── bottompipe.png        # Bottom pipe sprite
└── README.md             # Project documentation
Note: Make sure all image files are located in the exact same folder as the .java files when running the game.

Requirements:-
Java Development Kit (JDK): Version 8 or higher.

Operating System: Windows, macOS, or Linux.

Environment: Command Prompt or Terminal.

How to Run the Project:-
On Windows:-
Install Java: Download and install the JDK from Oracle's website.

Open Command Prompt and navigate to your project directory:

cd Desktop\Flappy-Bird

Compile the code:-

javac *.java
Run the game:

java App
On macOS / Linux:-
Open Terminal and navigate to your project directory:

Bash
cd ~/Desktop/Flappy-Bird
Compile the code:

Bash
javac *.java
Run the game:

Bash
java App

Controls:-
[ SPACEBAR ] : Make the bird jump.

Goal: Avoid hitting the pipes or the ground and try to get the highest score!

Troubleshooting:-
Error: javac is not recognized as an internal or external command (Windows)
This means Java is not added to your system's PATH.

Open Windows Search and type "Edit the system environment variables".

Click on Environment Variables.

Under System Variables, find and edit Path.

Add the path to your JDK bin folder.

Restart Command Prompt and try compiling again.

Author:-
Gaurav
B.Tech CSE (Data Science).
