from torch.utils.data import Dataset, DataLoader

import torch
import torch.nn as nn
from torch.autograd import Variable
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import torch.optim as optim

# Global Parameters:
BATCH_SIZE = 10
IS_CUDA    = False
LR         = 0.03
MOMENTUM   = 1e-6
EPOCHS      = 10
LOG_IN     = 50

# Load Dataset
def load_dataset(txt_filepath):
    
    # PLace to load the informaton we have
    #features = np.loadtxt(txt_filepath).T
    data = np.random.randint(5, size=(1000, 19))
    target = np.random.randint(6, size=1000)
    return data, target

# Global objects:
class PokerDataset(Dataset):

    def __init__(self, txt_filepath):
        self.data, self.target = load_dataset(txt_filepath)
    def __getitem__(self, index):
        return self.data[index,:], self.target[index] 
    def __len__(self):
        return self.data.shape[0]

# Network Architecture:
class BlueNet(nn.Module):

    def __init__(self):
        super(BlueNet, self).__init__()
        self.layer1 = nn.Linear(19, 38)
        self.layer2 = nn.Linear(38, 76)
        self.layer3 = nn.Linear(76,24)
        self.layer4 = nn.Linear(24, 12)
        self.layer5 = nn.Linear(12, 6)

        self.relu = nn.ReLU()
        self.tanh = nn.Tanh()

    def forward(self, x):
        fc1 = self.relu(self.layer2(self.relu((self.layer1(x)))))
        out_x = self.tanh(self.layer5(self.relu(self.layer4(self.relu((self.layer3(fc1)))))))
        return out_x


train_set = PokerDataset(0)
train_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)

model = BlueNet()
if IS_CUDA:
    model.cuda()

optimizer = optim.Adam(model.parameters(), lr=LR, weight_decay=MOMENTUM)

# Use MSE as Reconstrcution Loss
criterion = nn.CrossEntropyLoss()

def train(epoch):

    model.train()

    for batch_idx, (data, target) in enumerate(train_loader):
        # reshape to vector
        #data = data.view(data.size(0), -1)
        # move to cuda if available
        if IS_CUDA:
            data = data.cuda()
        # convert to Variable
        data = Variable(data.type(torch.FloatTensor))
        target = Variable(target.type(torch.LongTensor))
        # forward: evaluate with model
        output = model(data)
        loss = criterion(output, target)
        # backward: compute gradient and update weights
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if batch_idx % LOG_IN == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.data[0]))

best_acc = 0
# run training
for epoch in range(EPOCHS):
    train(epoch)
    #test_loss = test(show_plot=epoch%10 == 1)
    #if test_loss < best_loss:
    #    best_loss = test_loss
    #    if args.is_noisy:
    #        torch.save(model.state_dict(), 'best_fc_denoising_autoencoder.pth')
    #    else:
    #        torch.save(model.state_dict(), 'best_fc_autoencoder.pth')