import numpy as np
import random
from puyo_nn import PuyoNeuralNetwork
from puyopuyo import GameState, PuyoGame  # Import your game logic

class PuyoTrainer:
    def __init__(self, input_size, hidden_size, output_size, learning_rate=0.001, gamma=0.99, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01):
        """
        Initialize the training environment and the neural network.
        :param input_size: Number of features (input to the neural network).
        :param hidden_size: Number of hidden neurons.
        :param output_size: Number of actions (outputs of the neural network).
        :param learning_rate: Learning rate for the neural network.
        :param gamma: Discount factor for future rewards.
        :param epsilon: Initial exploration rate for epsilon-greedy policy.
        :param epsilon_decay: Factor by which epsilon decreases after each episode.
        :param epsilon_min: Minimum value of epsilon.
        """
        self.nn = PuyoNeuralNetwork(input_size, hidden_size, output_size, learning_rate)
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.actions = ['left', 'right', 'rotate', 'drop']  # Correspond to outputs of the neural network

    def extract_features(self, state):
        """
        Convert the game state into a feature vector for the neural network.
        :param state: The GameState object.
        :return: A 1D numpy array of features.
        """
        grid_flattened = np.array([1 if cell else 0 for row in state.grid for cell in row])
        current_puyo_pos = np.array(state.current_puyo).flatten() if state.current_puyo else np.zeros(6)
        return np.concatenate([grid_flattened, current_puyo_pos, [state.score]])

    def choose_action(self, state):
        """
        Choose an action using epsilon-greedy policy.
        :param state: The current game state.
        :return: An action from ['left', 'right', 'rotate', 'drop'].
        """
        if np.random.rand() < self.epsilon:
            return random.choice(self.actions)  # Explore
        features = self.extract_features(state).reshape(1, -1)
        q_values = self.nn.predict(features)
        return self.actions[np.argmax(q_values)]  # Exploit

    def train(self, episodes=1000, max_steps=500):
        """
        Train the neural network using reinforcement learning.
        :param episodes: Number of training episodes.
        :param max_steps: Maximum steps per episode.
        """
        for episode in range(episodes):
            game = PuyoGame()  # Initialize a new game
            total_reward = 0

            for step in range(max_steps):
                # Extract current state features
                current_features = self.extract_features(game.state)

                # Choose an action
                action = self.choose_action(game.state)

                # Simulate action
                game.process_input(action)
                game.update()

                # Check if the game is over
                if not game.is_running():
                    reward = -10  # Penalize for game over
                    self.update_nn(current_features, reward, None, action)
                    break

                # Compute reward based on score improvement
                reward = game.state.score - total_reward
                total_reward = game.state.score

                # Extract next state features
                next_features = self.extract_features(game.state)

                # Update neural network
                self.update_nn(current_features, reward, next_features, action)

            # Decay exploration rate (epsilon)
            self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)

            print(f"Episode {episode + 1}/{episodes}: Total Reward: {total_reward}, Epsilon: {self.epsilon:.4f}")


    def update_nn(self, current_features, reward, next_features, action):
        """
        Perform a Q-learning update for the neural network.
        :param current_features: Features of the current state.
        :param reward: Reward received after taking the action.
        :param next_features: Features of the next state.
        """
        current_features = current_features.reshape(1, -1)
        q_values = self.nn.predict(current_features)

        if next_features is None:
            target = reward  # Terminal state
        else:
            next_features = next_features.reshape(1, -1)
            next_q_values = self.nn.predict(next_features)
            target = reward + self.gamma * np.max(next_q_values)

        # Update the Q-value for the action taken
        action_index = self.actions.index(action)
        q_values[0, action_index] = target

        # Train the neural network
        self.nn.backward(q_values, self.nn.forward(current_features))

if __name__ == "__main__":
    # Define the input size based on game state representation
    grid_size = 6 * 12  # 6x12 grid
    input_size = grid_size + 6 + 1  # Grid + current puyo position + score
    hidden_size = 64
    output_size = 4

    trainer = PuyoTrainer(input_size, hidden_size, output_size)
    trainer.train(episodes=500)
