# 🐦 Flappy Bird - Java (Swing)

Flappy Bird is a simple, lightweight desktop version of the classic Flappy Bird game built from scratch using Java Swing and AWT. In this game, the player controls a bird that must fly through an endless obstacle course of pipes without colliding with them. The main objective is to guide the bird safely through the gaps between the pipes and achieve the highest possible score.

This project includes smooth physics for responsive bird movement and gravity simulation, infinite gameplay through continuous and random pipe generation, accurate collision detection between the bird, pipes, and ground, real-time score tracking whenever the bird successfully passes through pipes, custom graphical rendering for the background, bird, and pipes using image sprites, and intuitive keyboard controls that make the gameplay simple and interactive.

The project consists of the main application entry point and window setup in App.java, while the core game logic including rendering, physics, collision detection, and pipe generation is handled in FlappyBird.java. The graphical assets such as flappybird.png, flappybirdbg.png, toppipe.png, and bottompipe.png are used for the bird, background, and pipe visuals. All these image files must be kept in the same folder as the Java files while running the game to ensure proper rendering.

To run this project, the system must have Java Development Kit (JDK) version 8 or higher installed. The game can be executed on Windows, macOS, or Linux using Command Prompt or Terminal. On Windows, open Command Prompt and navigate to the project directory using the command cd Desktop\Flappy-Bird. Compile the project by running javac *.java and then execute the game using java App. On macOS or Linux, open Terminal and navigate to the project directory using cd ~/Desktop/Flappy-Bird. Compile the code using javac *.java and run the game using java App.

The game is controlled using the SPACEBAR key which allows the bird to jump. The main goal is to avoid hitting the pipes or the ground and survive as long as possible to achieve the highest score.

If you encounter the error stating that 'javac is not recognized as an internal or external command' on Windows, it means Java is not added to your system's PATH environment variable. To fix this, open Windows Search and type "Edit the system environment variables", go to Environment Variables, find and edit the Path variable under System Variables, and add the path to your JDK bin folder such as C:\Program Files\Java\jdk-21\bin. Restart Command Prompt and try compiling again.

Author: Gaurav  
B.Tech CSE (Data Science)
