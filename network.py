import torch
from torch import nn
import numpy as np


# Here we define our model as a class
class LSTM(nn.Module):

    def __init__(self, input_dim, hidden_dim, batch_size, output_dim=1,
                 num_layers=2):
        super(LSTM, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.batch_size = batch_size
        self.num_layers = num_layers

        # Define the LSTM layer
        self.lstm = nn.LSTM(self.input_dim, self.hidden_dim, self.num_layers)

        # Define the output layer
        self.linear = nn.Linear(self.hidden_dim, output_dim)

    def init_hidden(self):
        # This is what we'll initialise our hidden state as
        return (torch.zeros(self.num_layers, self.batch_size, self.hidden_dim),
                torch.zeros(self.num_layers, self.batch_size, self.hidden_dim))

    def forward(self, input):
        # Forward pass through LSTM layer
        # shape of lstm_out: [input_size, batch_size, hidden_dim]
        # shape of self.hidden: (a, b), where a and b both
        # have shape (num_layers, batch_size, hidden_dim).
        lstm_out, self.hidden = self.lstm(input.view(len(input), self.batch_size, -1))

        # Only take the output from the final timetep
        # Can pass on the entirety of lstm_out to the next layer if it is a seq2seq prediction
        y_pred = self.linear(lstm_out[-1].view(self.batch_size, -1))
        return y_pred.view(-1)


model = LSTM(1, 64, batch_size=1, output_dim=1, num_layers=2)

xor_data = np.array([(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)])
xor_sequence = np.ravel(xor_data[np.random.randint(4, size=1001)])

X = xor_sequence[:-3]
y = xor_sequence[1:-2]
X = torch.from_numpy(X)
y = torch.from_numpy(y)
data = zip(X, y)

loss_fn = torch.nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.1)

#####################
# Train model
#####################

num_epochs = 300

for t in range(num_epochs):
    for input_x, output_y in data:
        # Clear stored gradient
        model.zero_grad()

        # Initialise hidden state
        # Don't do this if you want your LSTM to be stateful
        # model.hidden = model.init_hidden()

        # Forward pass
        print(input_x, output_y)
        y_pred = model(input_x)

        loss = loss_fn(y_pred, output_y)
        if t % 100 == 0:
            print("Epoch ", t, "MSE: ", loss.item())

        # Zero out gradient, else they will accumulate between epochs
        optimizer.zero_grad()
        # Backward pass
        loss.backward()
        # Update parameters
        optimizer.step()
