import java.awt.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Random;
import javax.swing.*;

public class FlappyBird extends JPanel implements ActionListener, KeyListener {
    // Board dimensions
    private static final int BOARD_WIDTH = 360;
    private static final int BOARD_HEIGHT = 640;
    
    // Bird properties
    private static final int BIRD_X = BOARD_WIDTH / 8;
    private static final int BIRD_Y = BOARD_HEIGHT / 2;
    private static final int BIRD_WIDTH = 34;
    private static final int BIRD_HEIGHT = 24;
    
    // Pipe properties
    private static final int PIPE_WIDTH = 64;
    private static final int PIPE_HEIGHT = 512;
    private static final int PIPE_OPENING = BOARD_HEIGHT / 4;
    
    // Game physics
    private static final int INITIAL_GRAVITY = 1;
    private static final int JUMP_STRENGTH = -9;
    private static final int INITIAL_PIPE_VELOCITY = -4;
    private static final int INITIAL_SPAWN_DELAY = 1500;
    
    // Difficulty scaling
    private static final int SCORE_FOR_SPEED_INCREASE = 5;
    private static final double SPEED_MULTIPLIER = 1.15;
    private static final int MIN_SPAWN_DELAY = 1000;
    
    // Images
    private Image backgroundImg;
    private Image birdImg;
    private Image topPipeImg;
    private Image bottomPipeImg;

    // Bird class with animation support
    class Bird {
        int x = BIRD_X;
        int y = BIRD_Y;
        int width = BIRD_WIDTH;
        int height = BIRD_HEIGHT;
        int velocityY = 0;
        double rotation = 0; // For visual rotation effect
        Image img;

        Bird(Image img) {
            this.img = img;
        }
        
        void jump() {
            velocityY = JUMP_STRENGTH;
        }
        
        void update() {
            velocityY += gravity;
            y += velocityY;
            y = Math.max(y, 0);
            
            // Calculate rotation based on velocity (-45 to +90 degrees)
            rotation = Math.min(Math.max(velocityY * 3, -45), 90);
        }
        
        void reset() {
            x = BIRD_X;
            y = BIRD_Y;
            velocityY = 0;
            rotation = 0;
        }
        
        Rectangle getBounds() {
            // Slightly smaller hitbox for more forgiving gameplay
            return new Rectangle(x + 2, y + 2, width - 4, height - 4);
        }
    }

    // Pipe class
    class Pipe {
        int x = BOARD_WIDTH;
        int y;
        int width = PIPE_WIDTH;
        int height = PIPE_HEIGHT;
        Image img;
        boolean passed = false;

        Pipe(Image img, int y) {
            this.img = img;
            this.y = y;
        }
        
        void update() {
            x += velocityX;
        }
        
        boolean isOffScreen() {
            return x + width < 0;
        }
        
        Rectangle getBounds() {
            return new Rectangle(x, y, width, height);
        }
    }
    
    // Particle effect for collisions and scoring
    class Particle {
        double x, y;
        double velocityX, velocityY;
        Color color;
        int life;
        int maxLife;
        
        Particle(double x, double y, Color color) {
            this.x = x;
            this.y = y;
            this.color = color;
            this.maxLife = 20;
            this.life = maxLife;
            
            // Random velocity
            Random rand = new Random();
            this.velocityX = (rand.nextDouble() - 0.5) * 4;
            this.velocityY = (rand.nextDouble() - 0.5) * 4 - 2;
        }
        
        void update() {
            x += velocityX;
            y += velocityY;
            velocityY += 0.2; // Gravity
            life--;
        }
        
        boolean isDead() {
            return life <= 0;
        }
        
        void draw(Graphics2D g2d) {
            float alpha = (float) life / maxLife;
            g2d.setColor(new Color(color.getRed(), color.getGreen(), color.getBlue(),
                                  (int)(alpha * 255)));
            int size = 4;
            g2d.fillOval((int)x, (int)y, size, size);
        }
    }

    // Game objects
    private Bird bird;
    private ArrayList<Pipe> pipes;
    private ArrayList<Particle> particles;
    private Random random;
    
    // Game state
    private int velocityX = INITIAL_PIPE_VELOCITY;
    private int gravity = INITIAL_GRAVITY;
    private boolean gameOver = false;
    private boolean gameStarted = false;
    private boolean paused = false;
    private int score = 0;
    private int highScore = 0;
    private int lastSpeedIncreaseScore = 0;
    
    // Timers
    private Timer gameLoop;
    private Timer placePipeTimer;
    private int pipeSpawnDelay = INITIAL_SPAWN_DELAY;
    
    // Visual effects
    private int flashTimer = 0;
    private Color flashColor = null;

    FlappyBird() {
        setPreferredSize(new Dimension(BOARD_WIDTH, BOARD_HEIGHT));
        setFocusable(true);
        addKeyListener(this);

        loadImages();
        initGame();
        
        // Game loop - 60 FPS
        gameLoop = new Timer(1000 / 60, this);
        gameLoop.start();
    }
    
    private void loadImages() {
        try {
            backgroundImg = new ImageIcon(getClass().getResource("./flappybirdbg.png")).getImage();
            birdImg = new ImageIcon(getClass().getResource("./flappybird.png")).getImage();
            topPipeImg = new ImageIcon(getClass().getResource("./toppipe.png")).getImage();
            bottomPipeImg = new ImageIcon(getClass().getResource("./bottompipe.png")).getImage();
        } catch (Exception e) {
            System.err.println("Error loading images: " + e.getMessage());
            // Create colored rectangles as fallback
            backgroundImg = createColoredImage(BOARD_WIDTH, BOARD_HEIGHT, new Color(135, 206, 235));
            birdImg = createColoredImage(BIRD_WIDTH, BIRD_HEIGHT, Color.YELLOW);
            topPipeImg = createColoredImage(PIPE_WIDTH, PIPE_HEIGHT, Color.GREEN);
            bottomPipeImg = createColoredImage(PIPE_WIDTH, PIPE_HEIGHT, Color.GREEN);
        }
    }
    
    private Image createColoredImage(int width, int height, Color color) {
        Image img = new BufferedImage(width, height, BufferedImage.TYPE_INT_ARGB);
        Graphics g = img.getGraphics();
        g.setColor(color);
        g.fillRect(0, 0, width, height);
        g.dispose();
        return img;
    }
    
    private void initGame() {
        bird = new Bird(birdImg);
        pipes = new ArrayList<>();
        particles = new ArrayList<>();
        random = new Random();
        gameOver = false;
        gameStarted = false;
        paused = false;
        score = 0;
        velocityX = INITIAL_PIPE_VELOCITY;
        pipeSpawnDelay = INITIAL_SPAWN_DELAY;
        lastSpeedIncreaseScore = 0;
        
        // Stop and reset pipe timer
        if (placePipeTimer != null) {
            placePipeTimer.stop();
        }
    }
    
    private void startGame() {
        gameStarted = true;
        bird.jump();
        
        // Start pipe spawning
        placePipeTimer = new Timer(pipeSpawnDelay, e -> placePipes());
        placePipeTimer.start();
    }
    
    private void placePipes() {
        if (gameOver || paused) return;
        
        // Random pipe height
        int minY = -PIPE_HEIGHT * 3 / 4;
        int maxY = -PIPE_HEIGHT / 4;
        int randomPipeY = minY + random.nextInt(maxY - minY + 1);
        
        Pipe topPipe = new Pipe(topPipeImg, randomPipeY);
        pipes.add(topPipe);
        
        Pipe bottomPipe = new Pipe(bottomPipeImg, randomPipeY + PIPE_HEIGHT + PIPE_OPENING);
        pipes.add(bottomPipe);
    }
    
    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2d = (Graphics2D) g;
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        
        draw(g2d);
    }

    private void draw(Graphics2D g2d) {
        // Background
        g2d.drawImage(backgroundImg, 0, 0, BOARD_WIDTH, BOARD_HEIGHT, null);
        
        // Flash effect
        if (flashTimer > 0) {
            g2d.setColor(new Color(flashColor.getRed(), flashColor.getGreen(),
                                  flashColor.getBlue(), flashTimer * 15));
            g2d.fillRect(0, 0, BOARD_WIDTH, BOARD_HEIGHT);
            flashTimer--;
        }

        // Pipes
        for (Pipe pipe : pipes) {
            g2d.drawImage(pipe.img, pipe.x, pipe.y, pipe.width, pipe.height, null);
        }
        
        // Particles
        for (Particle particle : particles) {
            particle.draw(g2d);
        }

        // Bird with rotation
        drawRotatedBird(g2d, bird);
        
        // UI
        drawUI(g2d);
    }
    
    private void drawRotatedBird(Graphics2D g2d, Bird bird) {
        Graphics2D g2dCopy = (Graphics2D) g2d.create();
        
        int centerX = bird.x + bird.width / 2;
        int centerY = bird.y + bird.height / 2;
        
        g2dCopy.rotate(Math.toRadians(bird.rotation), centerX, centerY);
        g2dCopy.drawImage(bird.img, bird.x, bird.y, bird.width, bird.height, null);
        g2dCopy.dispose();
    }
    
    private void drawUI(Graphics2D g2d) {
        g2d.setColor(Color.WHITE);
        
        if (!gameStarted) {
            drawStartScreen(g2d);
        } else if (gameOver) {
            drawGameOverScreen(g2d);
        } else if (paused) {
            drawPauseScreen(g2d);
        } else {
            drawGameplayUI(g2d);
        }
    }
    
    private void drawStartScreen(Graphics2D g2d) {
        drawShadowedText(g2d, "Flappy Bird", BOARD_WIDTH / 2, BOARD_HEIGHT / 2 - 60,
                        new Font("Arial", Font.BOLD, 48), Color.WHITE);
        drawShadowedText(g2d, "Press SPACE to Start", BOARD_WIDTH / 2, BOARD_HEIGHT / 2 + 20,
                        new Font("Arial", Font.PLAIN, 20), Color.WHITE);
        
        if (highScore > 0) {
            drawShadowedText(g2d, "High Score: " + highScore, BOARD_WIDTH / 2, BOARD_HEIGHT / 2 + 60,
                            new Font("Arial", Font.PLAIN, 18), new Color(255, 215, 0));
        }
        
        // Instructions
        g2d.setFont(new Font("Arial", Font.PLAIN, 14));
        String[] instructions = {"Controls:", "SPACE - Jump", "P - Pause", "R - Restart"};
        int startY = BOARD_HEIGHT - 120;
        for (int i = 0; i < instructions.length; i++) {
            drawShadowedText(g2d, instructions[i], BOARD_WIDTH / 2, startY + i * 20,
                            new Font("Arial", Font.PLAIN, 14), Color.LIGHT_GRAY);
        }
    }
    
    private void drawGameOverScreen(Graphics2D g2d) {
        // Semi-transparent overlay
        g2d.setColor(new Color(0, 0, 0, 150));
        g2d.fillRect(0, 0, BOARD_WIDTH, BOARD_HEIGHT);
        
        drawShadowedText(g2d, "Game Over!", BOARD_WIDTH / 2, BOARD_HEIGHT / 2 - 80,
                        new Font("Arial", Font.BOLD, 48), Color.RED);
        drawShadowedText(g2d, "Score: " + score, BOARD_WIDTH / 2, BOARD_HEIGHT / 2 - 20,
                        new Font("Arial", Font.PLAIN, 32), Color.WHITE);
        drawShadowedText(g2d, "High Score: " + highScore, BOARD_WIDTH / 2, BOARD_HEIGHT / 2 + 20,
                        new Font("Arial", Font.PLAIN, 24), new Color(255, 215, 0));
        drawShadowedText(g2d, "Press SPACE to Restart", BOARD_WIDTH / 2, BOARD_HEIGHT / 2 + 80,
                        new Font("Arial", Font.PLAIN, 20), Color.WHITE);
    }
    
    private void drawPauseScreen(Graphics2D g2d) {
        g2d.setColor(new Color(0, 0, 0, 100));
        g2d.fillRect(0, 0, BOARD_WIDTH, BOARD_HEIGHT);
        
        drawShadowedText(g2d, "PAUSED", BOARD_WIDTH / 2, BOARD_HEIGHT / 2,
                        new Font("Arial", Font.BOLD, 48), Color.YELLOW);
        drawShadowedText(g2d, "Press P to Resume", BOARD_WIDTH / 2, BOARD_HEIGHT / 2 + 50,
                        new Font("Arial", Font.PLAIN, 20), Color.WHITE);
    }
    
    private void drawGameplayUI(Graphics2D g2d) {
        // Current score
        drawShadowedText(g2d, String.valueOf(score), 20, 40,
                        new Font("Arial", Font.BOLD, 40), Color.WHITE);
        
        // High score in corner
        if (highScore > 0) {
            String highScoreText = "Best: " + highScore;
            g2d.setFont(new Font("Arial", Font.PLAIN, 16));
            int textWidth = g2d.getFontMetrics().stringWidth(highScoreText);
            drawShadowedText(g2d, highScoreText, BOARD_WIDTH - textWidth / 2 - 10, 25,
                            new Font("Arial", Font.PLAIN, 16), new Color(255, 215, 0));
        }
        
        // Speed indicator
        if (score > 0 && score % SCORE_FOR_SPEED_INCREASE == 0) {
            int level = score / SCORE_FOR_SPEED_INCREASE + 1;
            drawShadowedText(g2d, "Level " + level, BOARD_WIDTH / 2, 30,
                            new Font("Arial", Font.BOLD, 18), new Color(0, 255, 0));
        }
    }
    
    private void drawShadowedText(Graphics2D g2d, String text, int x, int y, Font font, Color color) {
        g2d.setFont(font);
        FontMetrics fm = g2d.getFontMetrics();
        int textX = x - fm.stringWidth(text) / 2;
        
        // Shadow
        g2d.setColor(Color.BLACK);
        g2d.drawString(text, textX + 2, y + 2);
        
        // Text
        g2d.setColor(color);
        g2d.drawString(text, textX, y);
    }

    private void update() {
        if (!gameStarted || gameOver || paused) {
            return;
        }
        
        // Update bird
        bird.update();
        
        // Update particles
        particles.removeIf(Particle::isDead);
        for (Particle particle : particles) {
            particle.update();
        }
        
        // Update pipes
        Iterator<Pipe> iterator = pipes.iterator();
        while (iterator.hasNext()) {
            Pipe pipe = iterator.next();
            pipe.update();
            
            // Score when passing pipe
            if (!pipe.passed && bird.x > pipe.x + pipe.width) {
                score += 0.5;
                pipe.passed = true;
                
                // Create score particles
                if (score % 1 == 0) { // Every complete pipe set
                    createScoreParticles(pipe.x + pipe.width, BOARD_HEIGHT / 2);
                    flashTimer = 3;
                    flashColor = new Color(255, 255, 0);
                }
                
                // Increase difficulty
                increaseDifficulty();
            }
            
            // Check collision
            if (collision(bird, pipe)) {
                endGame();
                createCollisionParticles(bird.x + bird.width / 2, bird.y + bird.height / 2);
            }
            
            // Remove off-screen pipes
            if (pipe.isOffScreen()) {
                iterator.remove();
            }
        }
        
        // Check if bird hit ground or ceiling
        if (bird.y > BOARD_HEIGHT || bird.y < 0) {
            endGame();
            createCollisionParticles(bird.x + bird.width / 2, bird.y + bird.height / 2);
        }
    }
    
    private void increaseDifficulty() {
        int currentLevel = score / SCORE_FOR_SPEED_INCREASE;
        int lastLevel = lastSpeedIncreaseScore / SCORE_FOR_SPEED_INCREASE;
        
        if (currentLevel > lastLevel) {
            velocityX = (int)(INITIAL_PIPE_VELOCITY * Math.pow(SPEED_MULTIPLIER, currentLevel));
            pipeSpawnDelay = Math.max(MIN_SPAWN_DELAY,
                                     (int)(INITIAL_SPAWN_DELAY / Math.pow(1.1, currentLevel)));
            
            // Restart timer with new delay
            if (placePipeTimer != null) {
                placePipeTimer.stop();
                placePipeTimer = new Timer(pipeSpawnDelay, e -> placePipes());
                placePipeTimer.start();
            }
            
            lastSpeedIncreaseScore = score;
        }
    }
    
    private void createScoreParticles(int x, int y) {
        for (int i = 0; i < 10; i++) {
            particles.add(new Particle(x, y, new Color(255, 215, 0)));
        }
    }
    
    private void createCollisionParticles(int x, int y) {
        for (int i = 0; i < 20; i++) {
            particles.add(new Particle(x, y, Color.RED));
        }
        flashTimer = 5;
        flashColor = new Color(255, 0, 0);
    }

    private boolean collision(Bird bird, Pipe pipe) {
        return bird.getBounds().intersects(pipe.getBounds());
    }
    
    private void endGame() {
        gameOver = true;
        placePipeTimer.stop();
        
        // Update high score
        if (score > highScore) {
            highScore = score;
        }
    }

    @Override
    public void actionPerformed(ActionEvent e) {
        update();
        repaint();
    }

    @Override
    public void keyPressed(KeyEvent e) {
        int keyCode = e.getKeyCode();
        
        // Space key
        if (keyCode == KeyEvent.VK_SPACE) {
            if (!gameStarted) {
                startGame();
            } else if (gameOver) {
                initGame();
            } else if (!paused) {
                bird.jump();
            }
        }
        
        // Pause
        if (keyCode == KeyEvent.VK_P && gameStarted && !gameOver) {
            paused = !paused;
            if (paused) {
                placePipeTimer.stop();
            } else {
                placePipeTimer.start();
            }
        }
        
        // Restart
        if (keyCode == KeyEvent.VK_R) {
            initGame();
        }
    }

    @Override
    public void keyTyped(KeyEvent e) {}

    @Override
    public void keyReleased(KeyEvent e) {}
}
