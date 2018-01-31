from torch.utils.data import Dataset, DataLoader
from torch.autograd import Variable
import torch
import torch.nn as nn
import numpy as np
import random as rand
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import torch.optim as optim
import torch.nn.functional as F

# Global Parameters:
BATCH_SIZE = 512
IS_CUDA    = False
LR         = 0.01
MOMENTUM   = 1e-6
EPOCHS      = 100
LOG_IN     = 50

# Load Dataset
def load_dataset(path):
    
    # PLace to load the informaton we have
#    features = np.loadtxt(txt_filepath)
#    num_features = np.shape(features)[1]
#    target = features[:,-1]
#    data = features[:, range(num_features -1)]

    # If anything needs to be subtracted
    # data[:,i] = np.subtract(data[:,i], data[:,j])
    # data[:,i] = np.subtract(data[:,i], data[:,j])
    # data[:,i] = np.subtract(data[:,i], data[:,j])
    
    data = []
    target = []
    for _ in range(1000):
        for i in range(1, 7):
            data.append(np.random.randint(low = 100*(i), high = 100*(i+1)*1, size=20))
            target.append(i-1)
    return np.array(data), np.array(target)

# Global objects:
class PokerDataset(Dataset):

    def __init__(self, txt_filepath):
        self.data, self.target = load_dataset(txt_filepath)
        print(np.shape(self.data))
    def __getitem__(self, index):
        return self.data[index,:], self.target[index] 
    def __len__(self):
        return self.data.shape[0]

# Network Architecture:
class BlueNet_all(nn.Module):

    def __init__(self):
        super(BlueNet_all, self).__init__()
        self.layer1 = nn.Linear(20, 40)
        self.layer2 = nn.Linear(40, 120)
        self.layer3 = nn.Linear(120, 60)
        self.layer4 = nn.Linear(60, 30)
        self.layer5 = nn.Linear(30, 6)

        self.relu = nn.ReLU()
        self.softplus = nn.Softplus()

    def forward(self, x):
        fc1 = F.relu(self.layer2(self.relu((self.layer1(x)))))
        out_x = self.layer5(self.relu(self.layer4(self.relu((self.layer3(fc1))))))
        return out_x

train_set = PokerDataset(0)
train_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)

model = BlueNet_all()
if IS_CUDA:
    model.cuda()

optimizer = optim.Adam(model.parameters(), lr=LR)

# Use MSE as Reconstrcution Loss
criterion = nn.CrossEntropyLoss()

# Train loop
def train(epoch):

    model.train()

    for _, (data, target) in enumerate(train_loader):
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
            # Check accuracy rate
            #predict = torch.max(output, 1)[1]
            #predict = predict.data.numpy().squeeze() 
            #target = target.data.numpy()
            #accuracy = sum(predict == target)
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.data[0]))

# define prediction
def prediction(show_plot=False):
    best_loss = 100
    predict_target = model(test_data)
    predict = torch.max(predict_target, 1)[1]
    predict = predict.data.numpy().squeeze() 
    if test_target:
        loss = criterion(predict_target, test_target)
        if test_loss < best_loss:
            torch.save(model.state_dict(), 'best_predictor.pth')
        return predict[:]

best_loss = 0
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