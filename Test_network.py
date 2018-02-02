from torch.utils.data import Dataset, DataLoader
from torch.autograd import Variable
import torch
import torch.nn as nn
import numpy as np
import random as rand
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import torch.optim as optim
import torch.nn.functional as F
from sklearn.metrics import confusion_matrix
import pandas as pd

# Global Parameters:
BATCH_SIZE = 128
IS_CUDA    = False
LR         = 0.02
MOMENTUM   = 1e-6
EPOCHS      = 20
LOG_IN     = 1000
# Load Dataset
def load_dataset(path, mask):
    
    # Type 0:
    # Attributes: tournum, gamenum, phase, betidx, name, style, betact, amt, blind, balance, pot]+ list(comm_cards + list(hole_cards)
    #             (0),     (1),     (2),   (3),    (4),  (5),   (6),    (7), (8),    (9),   (10) - (11) -23)   
    
    # Type 1:
    # Attributes tournum: gamenum, phase, betidx, name, style, betact, amt, blind, balance, pot, prob
    #             (0),     (1),   (2),    (3),  (4),   (5),    (6), (7),   (8),     (9),(10)
    
    data_mask = [[2, 3] + range(7, 25), [2, 3] + range(7, 12)] 
    target_mask = 5

    data = np.genfromtxt(path, delimiter = ',', usecols = data_mask[mask])
    act = np.genfromtxt(path, delimiter = ',', usecols = 6, dtype = str)
    target = np.genfromtxt(path, delimiter = ',', usecols = target_mask, dtype = np.int)

    act_map = {'f':0, 'c':1, 'k':1, 'b':2, 'r':2}
    for i in range(len(act)):
        act[i] = act_map[act[i]]
    data = np.insert(data, 0, act, axis = 1)
    
    # Delete pre-flop
    #del_pf_mask = [i for i in range(len(data)) if data[i, 1] == 0]
    #data = np.delete(data, del_pf_mask, 0) 
    #target = np.delete(target, del_pf_mask, 0) 
    
    # Adjust non-fold balance
    # If anything needs to be added or subtracted
    nf_mask = [i for i in range(len(data)) if data[i, 0] != 0]
    data[nf_mask,5]  = np.add(data[nf_mask,5], data[nf_mask,3])
    data[nf_mask,5]  = np.divide(data[nf_mask,3], data[nf_mask,5])
    data[nf_mask,6] = np.subtract(data[nf_mask,6], data[nf_mask,3])
    data[nf_mask,6] = np.divide(data[nf_mask,3], data[nf_mask,6])
    data[:,3] = np.divide(data[:,3], data[:,4])
    target = np.subtract(target, 1)
    
    mask1 = [i for i in range(len(target)) if target[i] == 0]
    mask2 = [i for i in range(len(target)) if target[i] == 1]
    mask3 = [i for i in range(len(target)) if target[i] == 2]
    mask4 = [i for i in range(len(target)) if target[i] == 3]
    mask5 = [i for i in range(len(target)) if target[i] == 4]
    mask6 = [i for i in range(len(target)) if target[i] == 5]
    rand.shuffle(mask1)
    rand.shuffle(mask2)
    rand.shuffle(mask3)
    rand.shuffle(mask4)
    rand.shuffle(mask5)
    rand.shuffle(mask6)
    
    min_to_take = min(len(mask1), len(mask2), len(mask3), len(mask4), len(mask5), len(mask6))
    min_to_take = 3000
    print('The number of data to be taken from each class = {}'.format(min_to_take))
    total_mask = mask1[0:min_to_take] + mask2[0:min_to_take] + mask3[0:min_to_take] + mask4[0:min_to_take] + mask5[0:min_to_take] + mask6[0:min_to_take]
    
    data = data[total_mask, :]
    target = target[total_mask]
    
    print('Shape of data: {}, shape of target: {}'.format(np.shape(data), np.shape(target)))
    # Type 0:
    # Selcted attributes: betact, phase, betidx, blind-r, blind, bal-r,   pot-r + list(comm_cards + list(hole_cards)
    #                     (0),    (1),   (2),    (3),     (4),   (5),     (6),    (7) - (20)
    
    # Type 1:
    # Selcted attributes: betact, phase, betidx, blind-r, blind, bal-r,   pot-r + prob
    #                     (0),    (1),   (2),    (3),     (4),   (5),     (6),    (7)
    return data, target    

# Global Parameters:
class PokerDataset(Dataset):

    def __init__(self, txt_filepath, mask):
        self.data, self.target = load_dataset(txt_filepath, mask)
    def __getitem__(self, index):
        return self.data[index,:], self.target[index] 
    def __len__(self):
        return self.data.shape[0]

train_set0 = PokerDataset('./log/tourney_log20180201.txt', mask = 0)
#train_set2 = PokerDataset('./log/tourney2_log20180201.txt', mask = 1)
train_loader0 = DataLoader(train_set0, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)
#train_loader2 = DataLoader(train_set2, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)

# Network Architecture of different configuration:

class BlueNet_all6a(nn.Module):

    def __init__(self):
        super(BlueNet_all6a, self).__init__()
        self.l1 = nn.Linear(21, 42)
        self.l2 = nn.Linear(42, 84)
        self.l3 = nn.Linear(84, 84)
        self.l4 = nn.Linear(84, 84)
        self.l5 = nn.Linear(84, 42)
        self.l6 = nn.Linear(42, 21)
        self.l7 = nn.Linear(21, 6)

        self.relu = nn.ReLU()
        self.softmax = nn.Softmax()

    def forward(self, x):
        fc1 = self.relu(self.l3(self.relu(self.l2(self.relu(self.l1(x))))))
        out_x = self.softmax(self.l7(self.relu(self.l6(self.relu(self.l5(self.relu(self.l4(fc1))))))))
        return out_x

class BlueNet_all6b(nn.Module):

    def __init__(self):
        super(BlueNet_all6b, self).__init__()
        self.l1 = nn.Linear(21, 80)
        self.l2 = nn.Linear(80, 240)
        self.l3 = nn.Linear(240, 480)
        self.l4 = nn.Linear(480, 240)
        self.l5 = nn.Linear(240, 80)
        self.l6 = nn.Linear(80, 20)
        self.l7 = nn.Linear(20, 6)

        self.relu = nn.ReLU()
        self.softmax = nn.Softmax()

    def forward(self, x):
        fc1 = self.relu(self.l3(self.relu(self.l2(self.relu(self.l1(x))))))
        out_x = self.softmax(self.l7(self.relu(self.l6(self.relu(self.l5(self.relu(self.l4(fc1))))))))
        return out_x
    
class BlueNet_all4a(nn.Module):

    def __init__(self):
        super(BlueNet_all4a, self).__init__()
        self.l1 = nn.Linear(21, 42)
        self.l2 = nn.Linear(42, 84)
        self.l3 = nn.Linear(84, 42)
        self.l4 = nn.Linear(42, 21)
        self.l5 = nn.Linear(21, 6)

        self.relu = nn.ReLU()
        self.softmax = nn.Softmax()

    def forward(self, x):
        fc1 = F.relu(self.l2(self.relu((self.l1(x)))))
        out_x = self.softmax(self.l5(self.relu(self.l4(self.relu((self.l3(fc1)))))))
        return out_x

class BlueNet_all4b(nn.Module):

    def __init__(self):
        super(BlueNet_all4b, self).__init__()
        self.l1 = nn.Linear(21, 60)
        self.l2 = nn.Linear(60, 120)
        self.l3 = nn.Linear(120, 60)
        self.l4 = nn.Linear(60, 20)
        self.l5 = nn.Linear(20, 6)

        self.relu = nn.ReLU()
        self.softmax = nn.Softmax()

    def forward(self, x):
        fc1 = F.relu(self.l2(self.relu((self.l1(x)))))
        out_x = self.softmax(self.l5(self.relu(self.l4(self.relu((self.l3(fc1)))))))
        return out_x
    
class BlueNet_all2a(nn.Module):

    def __init__(self):
        super(BlueNet_all2a, self).__init__()
        self.l1 = nn.Linear(21, 42)
        self.l2 = nn.Linear(42, 21)
        self.l3 = nn.Linear(21, 6)

        self.relu = nn.ReLU()
        self.softmax = nn.Softmax()

    def forward(self, x):
        fc1 = F.relu((self.l1(x)))
        out_x = self.softmax(self.l3(self.relu((self.l2(fc1)))))
        return out_x

class BlueNet_all2b(nn.Module):

    def __init__(self):
        super(BlueNet_all2b, self).__init__()
        self.l1 = nn.Linear(21, 60)
        self.l2 = nn.Linear(60, 40)
        self.l3 = nn.Linear(40, 6)

        self.relu = nn.ReLU()
        self.softmax = nn.Softmax()

    def forward(self, x):
        fc1 = F.relu((self.l1(x)))
        out_x = self.softmax(self.l3(self.relu((self.l2(fc1)))))
        return out_x

class BlueNet_prob(nn.Module):

    def __init__(self):
        super(BlueNet_prob, self).__init__()
        self.l1 = nn.Linear(8, 16)
        self.l2 = nn.Linear(16, 32)
        self.l3 = nn.Linear(32, 16)
        self.l4 = nn.Linear(16, 6)

        self.relu = nn.ReLU()
        self.softmax = nn.Softmax()

    def forward(self, x):
        fc1 = F.relu(self.l2(self.relu((self.l1(x)))))
        out_x = self.softmax(self.l4(self.relu((self.l3(fc1)))))
        return out_x

# Model Selection
models_sel= [BlueNet_all6a(), BlueNet_all4a(), BlueNet_all2a()]
best_model = 0
best_acc = 0
# Visualization of training curve
training_curve = []
plt.figure
plt.xlabel('epoch')
plt.ylabel('Accuract Rate')
plt.title('Growth of Accuracy Rate with different Network Models')

# Train loop
def train(epoch, best_acc):

    model.train()
    acc_result = 0
    for batch_idx, (data, target) in enumerate(train_loader0):
        # reshape to vector
        #data = data.view(data.size(0), -1)
        # move to cuda if available
        if IS_CUDA:
            data = data.cuda()
            target = target.cuda()
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
        # Check accuracy rate
        predict = torch.max(output, 1)[1]
        predict = predict.data.numpy().squeeze() 
        target = target.data.numpy()
        accuracy = sum(predict == target)
        acc_result += accuracy
        if batch_idx % LOG_IN == 0:
            #print(predict)
            #print(target)
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tAccuracy Rate: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader0.dataset),
                100. * batch_idx / len(train_loader0), accuracy/float(len(data))))
            
    model_tc.append(float(acc_result)/len(train_loader0.dataset))  
    
    if model_tc[-1] > best_acc:
        return model_tc[-1]
    else:
        return 0
    
# define prediction
def prediction():
    prediction_list = []
    for batch_x, _ in train_loader0:
        if IS_CUDA:
            batch_x = batch_x.cuda()
        best_loss = 100
        batch_x = Variable(batch_x.type(torch.FloatTensor))
        predict_target = best_model(batch_x)
        predict = torch.max(predict_target, 1)[1]
        predict = predict.data.numpy().squeeze()
        
        prediction_list.append(predict)
    return np.concatenate(prediction_list)

for model in models_sel:

    if IS_CUDA:
        model.cuda()

    optimizer = optim.Adam(model.parameters(), lr=LR)

    # Loss criterion
    criterion = nn.CrossEntropyLoss()
    model_tc = []

    # run training
    for epoch in range(EPOCHS):
        update_acc = train(epoch, best_acc)
        if update_acc != 0:
            best_acc = update_acc
            best_model = model

    training_curve.append(model_tc) 

curve_name = ['6a', '4a', '2a']
for i in range(len(training_curve)):
    plt.plot(range(EPOCHS), training_curve[i], label = 'Model{}'.format(curve_name[i]))
plt.legend()
plt.savefig('./result/accuracy_growth.png')
#plt.show()

confumat = confusion_matrix(prediction(), train_set0.target)
pd.DataFrame(confumat)
