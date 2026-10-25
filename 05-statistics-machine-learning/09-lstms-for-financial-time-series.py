"""LSTMs for Financial Time Series

Post: https://mathforfinance.com/lstms-for-financial-time-series/

Code snippets from the post, in the order they appear. Each "# %%" marks a
cell (runs as a cell in VS Code / Jupyter). Some snippets use variables that
the post defines in the text or in an earlier snippet.
"""

# %% Snippet 1
import torch
from torch import nn

class VolLSTM(nn.Module):
    def __init__(self, hidden=16):
        super().__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=hidden, batch_first=True)
        self.head = nn.Linear(hidden, 1)

    def forward(self, x):                     # x: (batch, 20 days, 1 feature)
        out, _ = self.lstm(x)
        return self.head(out[:, -1, :]).squeeze(-1)   # use the last hidden state

model = VolLSTM()
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.MSELoss()

for epoch in range(30):
    model.train()
    for i in range(0, len(X_train), 64):     # mini-batches, in time order
        xb, yb = X_train[i:i + 64], y_train[i:i + 64]
        opt.zero_grad()
        loss = loss_fn(model(xb), yb)
        loss.backward()
        opt.step()
