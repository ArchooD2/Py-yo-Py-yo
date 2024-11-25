import numpy as np

class PuyoNeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size, learning_rate=0.001):
        """
        Initialize a simple feedforward neural network.
        :param input_size: Number of input neurons (features).
        :param hidden_size: Number of hidden neurons.
        :param output_size: Number of output neurons (actions).
        :param learning_rate: Learning rate for gradient descent.
        """
        # Initialize weights and biases
        self.weights_input_hidden = np.random.randn(input_size, hidden_size) * 0.01
        self.bias_hidden = np.zeros((1, hidden_size))
        self.weights_hidden_output = np.random.randn(hidden_size, output_size) * 0.01
        self.bias_output = np.zeros((1, output_size))

        # Learning rate
        self.learning_rate = learning_rate

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        return x * (1 - x)

    def forward(self, inputs):
        """
        Perform a forward pass of the neural network.
        :param inputs: Input data (features).
        :return: Output predictions.
        """
        self.input_layer = inputs
        self.hidden_layer = self.sigmoid(np.dot(self.input_layer, self.weights_input_hidden) + self.bias_hidden)
        self.output_layer = self.sigmoid(np.dot(self.hidden_layer, self.weights_hidden_output) + self.bias_output)
        return self.output_layer

    def backward(self, true_output, predicted_output):
        """
        Perform a backward pass (backpropagation) to update weights and biases.
        :param true_output: True labels or desired outputs.
        :param predicted_output: Predicted outputs from the forward pass.
        """
        # Calculate output error
        output_error = true_output - predicted_output
        output_delta = output_error * self.sigmoid_derivative(predicted_output)

        # Calculate hidden layer error
        hidden_error = np.dot(output_delta, self.weights_hidden_output.T)
        hidden_delta = hidden_error * self.sigmoid_derivative(self.hidden_layer)

        # Update weights and biases
        self.weights_hidden_output += self.learning_rate * np.dot(self.hidden_layer.T, output_delta)
        self.bias_output += self.learning_rate * np.sum(output_delta, axis=0, keepdims=True)
        self.weights_input_hidden += self.learning_rate * np.dot(self.input_layer.T, hidden_delta)
        self.bias_hidden += self.learning_rate * np.sum(hidden_delta, axis=0, keepdims=True)

    def train(self, inputs, true_output, epochs=1000):
        """
        Train the neural network on the provided data.
        :param inputs: Training input data.
        :param true_output: Training output labels.
        :param epochs: Number of training iterations.
        """
        for epoch in range(epochs):
            predicted_output = self.forward(inputs)
            self.backward(true_output, predicted_output)
            if epoch % 100 == 0:
                loss = np.mean((true_output - predicted_output) ** 2)
                print(f"Epoch {epoch}/{epochs} - Loss: {loss:.6f}")

    def predict(self, inputs):
        """
        Make predictions based on the current state of the neural network.
        :param inputs: Input data for prediction.
        :return: Predicted outputs.
        """
        return self.forward(inputs)


# Example usage: Testing the neural network module
if __name__ == "__main__":
    # Define a neural network with 10 input features, 16 hidden neurons, and 4 outputs
    nn = PuyoNeuralNetwork(input_size=10, hidden_size=16, output_size=4)

    # Create dummy data for training
    X_train = np.random.rand(100, 10)  # 100 samples with 10 features each
    y_train = np.random.randint(0, 2, (100, 4))  # 100 samples with binary outputs for 4 actions

    # Train the neural network
    nn.train(X_train, y_train, epochs=100000)

    # Make a prediction
    test_input = np.random.rand(1, 10)  # Single test input
    prediction = nn.predict(test_input)
    print(f"Test Input: {test_input}")
    print(f"Prediction: {prediction}")
