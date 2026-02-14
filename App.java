import javax.swing.*;
import java.awt.*;

public class App {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            int boardWidth = 360;
            int boardHeight = 640;

            JFrame frame = new JFrame("Flappy Bird - Enhanced Edition");
            frame.setSize(boardWidth, boardHeight);
            frame.setLocationRelativeTo(null);
            frame.setResizable(false);
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            
            // Set icon if available
            try {
                ImageIcon icon = new ImageIcon(App.class.getResource("./flappybird.png"));
                frame.setIconImage(icon.getImage());
            } catch (Exception e) {
                // Icon not found, continue without it
            }

            FlappyBird flappyBird = new FlappyBird();
            frame.add(flappyBird);
            frame.pack();
            flappyBird.requestFocus();
            frame.setVisible(true);
        });
    }
}
