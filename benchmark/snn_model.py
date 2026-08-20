"""Rate-coded spiking classifier on FashionMNIST (a standard benchmark).

We train a small MLP on FashionMNIST, then perform *rate-coded* inference: each image is
presented as a stream of Bernoulli-sampled binary frames (pixel intensity = spike
probability). Averaging the network's response over more frames (a larger "compute
budget" T) yields a less noisy, more accurate decision. Fewer frames = cheaper but noisier.

This gives inference a natural, monotonic accuracy-vs-energy knob (the number of frames T),
which the energy-management policy controls at run time. Higher energy reserve -> more
frames -> higher accuracy; low reserve -> fewer frames.

The dataset is loaded from a local cache (no download).
"""

from __future__ import annotations

import os

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms

DATA_ROOT = os.path.expanduser("~/IdeaProjects/edge-vision-quant/data")
WEIGHTS = os.path.join(os.path.dirname(__file__), "mlp.pt")
DEVICE = "cpu"


class MLP(nn.Module):
    def __init__(self, hidden: int = 256) -> None:
        super().__init__()
        self.fc1 = nn.Linear(784, hidden)
        self.fc2 = nn.Linear(hidden, 10)

    def forward(self, x):  # x: (B, 784) in [0,1]
        return self.fc2(F.relu(self.fc1(x)))


def _load(train: bool):
    tf = transforms.ToTensor()
    return datasets.FashionMNIST(DATA_ROOT, train=train, download=False, transform=tf)


def train_model(epochs: int = 2) -> MLP:
    model = MLP().to(DEVICE)
    if os.path.exists(WEIGHTS):
        model.load_state_dict(torch.load(WEIGHTS, map_location=DEVICE))
        return model
    ds = _load(train=True)
    loader = torch.utils.data.DataLoader(ds, batch_size=256, shuffle=True)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    model.train()
    for ep in range(epochs):
        for xb, yb in loader:
            xb = xb.view(xb.size(0), -1).to(DEVICE)
            opt.zero_grad()
            loss = F.cross_entropy(model(xb), yb.to(DEVICE))
            loss.backward()
            opt.step()
        print(f"  epoch {ep + 1}/{epochs} done")
    torch.save(model.state_dict(), WEIGHTS)
    return model


@torch.no_grad()
def correctness_by_budget(
    model: MLP,
    budgets: list[int],
    n_test: int = 1200,
    seed: int = 0,
):
    """Return (correct[n_test, len(budgets)] bool, labels[n_test]).

    correct[i, b] = was image i classified correctly using budgets[b] rate-coded frames?
    Budget 0 means "no compute" -> always incorrect (the device produced no answer).
    """
    ds = _load(train=False)
    n_test = min(n_test, len(ds))
    imgs = torch.stack([ds[i][0].view(-1) for i in range(n_test)]).to(DEVICE)  # (N,784)
    labels = np.array([ds[i][1] for i in range(n_test)])

    model.eval()
    g = torch.Generator(device=DEVICE).manual_seed(seed)
    max_b = max(budgets)
    logit_sum = torch.zeros(n_test, 10, device=DEVICE)

    # Cumulative accuracy at each checkpoint budget in one pass of max_b frames.
    checkpoints = {b: idx for idx, b in enumerate(budgets)}
    correct = np.zeros((n_test, len(budgets)), dtype=bool)
    if 0 in checkpoints:
        correct[:, checkpoints[0]] = False  # no compute -> wrong

    for t in range(1, max_b + 1):
        frame = torch.bernoulli(imgs, generator=g)      # (N,784) binary
        logit_sum += model(frame)
        if t in checkpoints:
            pred = logit_sum.argmax(dim=1).cpu().numpy()
            correct[:, checkpoints[t]] = pred == labels

    return correct, labels
