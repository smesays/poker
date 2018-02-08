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
BATCH_SIZE = 2048
IS_CUDA    = False
LR         = 0.01
MOMENTUM   = 1e-6
EPOCHS      = 3
LOG_IN     = 1000
# Load Dataset
def load_dataset(path, mask):
    
    # Type 0:
    # Attributes: tournum, gamenum, phase, betidx, name, style, betact, amt, blind, balance, pot]+ list(comm_cards + list(hole_cards)
    #             (0),     (1),     (2),   (3),    (4),  (5),   (6),    (7), (8),    (9),   (10) - (11) -23)   
    
    # Capture vs Random Info:
    
    #game_id_mask = np.genfromtxt('./log/agent_log20180201.txt', delimiter = ',', usecols = [0,2])
    #game_id_mask = [game_id_mask[i,0] for i in range(len(game_id_mask)) if game_id_mask[i,1] == 4]
    #game_id_mask = [i for i in range(len(data)) if data[i,0] in game_id_mask]
    
    # Delete pre-flop
    #del_pf_mask = [i for i in range(len(data)) if data[i, 1] == 0]
    #data = np.delete(data, del_pf_mask, 0) 
    #target = np.delete(target, del_pf_mask, 0) 
    
    # Capture useful information
    data_mask = [[0,2, 3] + range(7, 25), [0,2, 3] + range(7, 12)] 
    target_mask = 5
    
    # Load data
    data = np.genfromtxt(path, delimiter = ',', usecols = data_mask[mask])
    act = np.genfromtxt(path, delimiter = ',', usecols = 6, dtype = str)
    target = np.genfromtxt(path, delimiter = ',', usecols = target_mask, dtype = np.int)
    
    #data = data[game_id_mask, :]
    #target = target[ game_id_mask]
    #act = act[game_id_mask]
    data = np.delete(data, 0, 1)
    '''
    # Take minimum of classes and phases
    group_mask = {}
    min_to_take = []
    for g in range(1, 9): 
        group_mask[g] = {}
        for sg in range(1, 5):
            group_mask[g][sg]=[i for i in range(len(target)) if target[i] == int(g) and data[i, 0] == sg]
            rand.shuffle(group_mask[g][sg])
            min_to_take.append(len(group_mask[g][sg]))
    min_take = min(min_to_take)
    
    print('The number of data to be taken from each class = {}'.format(min_take*4))
    
    total_mask = group_mask[1][1][0:min_take] + group_mask[1][2][0:min_take] + group_mask[1][3][0:min_take] + group_mask[1][4][0:min_take]
    for g in range(2, 9):
         total_mask = total_mask + group_mask[g][1][0:min_take] + group_mask[g][2][0:min_take] + group_mask[g][3][0:min_take] + group_mask[g][4][0:min_take]
    '''
    total_mask = [i for i in range(len(target)) if target[i] in [1, 2, 3 , 5]]
    # Filter data with mask
    data = data[total_mask, :]
    target = target[total_mask]
    act = act[total_mask]
    map_mask2 = [i for i in range(len(target)) if target[i] == 5]
    target[map_mask2] = 4
    # Change string to int
    act_map = {'f':0, 'c':1, 'k':2, 'b':3, 'r':4}
    for i in range(len(act)):
        act[i] = act_map[act[i]]
    data = np.insert(data, 0, act, axis = 1)
    
    # Adjust non-fold balance
    # If anything needs to be added or subtracted
    nf_mask = [i for i in range(len(data)) if data[i, 0] != 0]
    data[nf_mask,5]  = np.add(data[nf_mask,5], data[nf_mask,3])
    data[nf_mask,5]  = np.divide(data[nf_mask,3], data[nf_mask,5])
    data[nf_mask,6] = np.subtract(data[nf_mask,6], data[nf_mask,3])
    data[nf_mask,6] = np.divide(data[nf_mask,3], data[nf_mask,6])
    data[:,3] = np.divide(data[:,3], data[:,4])
    target = np.subtract(target, 1)
    
    # Extend categorical variables
    phase_mat = np.zeros((len(data), 4))
    act_mat = np.zeros((len(data), 5))
    for i in range(len(phase_mat)):
        idx = int(data[i, 1]-1)
        phase_mat[i,idx] = 1
        idx = int(data[i, 0])
        act_mat[i, idx] = 1
    
    data = np.delete(data, 1, 1)
    #data = np.delete(data, 0, 1)
    #data = np.concatenate((act_mat, phase_mat, data), axis = 1)
    data = np.concatenate((phase_mat, data), axis = 1)
    
    print('Shape of data: {}, shape of target: {}'.format(np.shape(data), np.shape(target)))
    # Type 0:
    # Selcted attributes: betact, phase, betidx, blind-r, blind, bal-r,   pot-r + list(comm_cards + list(hole_cards)
    #                     (0-2),  (3-5), (6),    (7),     (8),   (9),     (10),   (11) - (20)
    return data, target    
  

# Global Parameters:
class PokerDataset(Dataset):

    def __init__(self, txt_filepath, mask):
        self.data, self.target = load_dataset(txt_filepath, mask)
    def __getitem__(self, index):
        return self.data[index,:], self.target[index] 
    def __len__(self):
        return self.data.shape[0]
    def __inout__(self):
        return self.data.shape[1], len(set(self.target))

train_set0 = PokerDataset('./log/tourney_log20180207.txt.gz', mask = 0)
test_set0 = PokerDataset('./log/tourney_log20180208.txt.gz', mask = 0)
train_loader0 = DataLoader(train_set0, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)
test_loader0 = DataLoader(test_set0, batch_size=BATCH_SIZE, shuffle=False, num_workers=2)

# Network Architecture of different configuration:

class BlueNet_all6a(nn.Module):

    def __init__(self, num_in, num_out):
        super(BlueNet_all6a, self).__init__()
        self.l1 = nn.Linear(num_in, num_in*2)
        self.l2 = nn.Linear(num_in*2, num_in*4)
        self.l3 = nn.Linear(num_in*4, num_in*4)
        self.l4 = nn.Linear(num_in*4, num_in*2)
        self.l5 = nn.Linear(num_in*2, num_in)
        self.l6 = nn.Linear(num_in, num_out*2)
        self.l7 = nn.Linear(num_out*2, num_out)

        self.relu = nn.ReLU()
        self.softmax = nn.Softmax()

    def forward(self, x):
        fc1 = self.relu(self.l3(self.relu(self.l2(self.relu(self.l1(x))))))
        out_x = self.softmax(self.l7(self.relu(self.l6(self.relu(self.l5(self.relu(self.l4(fc1))))))))
        return out_x

class BlueNet_all6b(nn.Module):

    def __init__(self, num_in, num_out):
        super(BlueNet_all6b, self).__init__()
        self.l1 = nn.Linear(num_in, num_in*2)
        self.l2 = nn.Linear(num_in*2, num_in*3)
        self.l3 = nn.Linear(num_in*3, num_in*3)
        self.l4 = nn.Linear(num_in*3, num_in*3)
        self.l5 = nn.Linear(num_in*3, num_in)
        self.l6 = nn.Linear(num_in, num_out*2)
        self.l7 = nn.Linear(num_out*2, num_out)

        self.relu = nn.ReLU()
        self.softmax = nn.Softmax()

    def forward(self, x):
        fc1 = self.relu(self.l3(self.relu(self.l2(self.relu(self.l1(x))))))
        out_x = self.softmax(self.l7(self.relu(self.l6(self.relu(self.l5(self.relu(self.l4(fc1))))))))
        return out_x
    
class BlueNet_all4a(nn.Module):

    def __init__(self, num_in, num_out):
        super(BlueNet_all4a, self).__init__()
        self.l1 = nn.Linear(num_in, num_in*2)
        self.l2 = nn.Linear(num_in*2, num_in*4)
        self.l3 = nn.Linear(num_in*4, num_in*2)
        self.l4 = nn.Linear(num_in*2, num_out*2)
        self.l5 = nn.Linear(num_out*2, num_out)

        self.relu = nn.ReLU()
        self.softmax = nn.Softmax()

    def forward(self, x):
        fc1 = F.relu(self.l2(self.relu((self.l1(x)))))
        out_x = self.softmax(self.l5(self.relu(self.l4(self.relu((self.l3(fc1)))))))
        return out_x

class BlueNet_all4b(nn.Module):

    def __init__(self, num_in, num_out):
        super(BlueNet_all4b, self).__init__()
        self.l1 = nn.Linear(num_in, num_in*2)
        self.l2 = nn.Linear(num_in*2, num_in*3)
        self.l3 = nn.Linear(num_in*3, num_in*2)
        self.l4 = nn.Linear(num_in*2, num_out*3)
        self.l5 = nn.Linear(num_out*3, num_out)

        self.relu = nn.ReLU()
        self.softmax = nn.Softmax()

    def forward(self, x):
        fc1 = F.relu(self.l2(self.relu((self.l1(x)))))
        out_x = self.softmax(self.l5(self.relu(self.l4(self.relu((self.l3(fc1)))))))
        return out_x
    
class BlueNet_all2a(nn.Module):

    def __init__(self, num_in, num_out):
        super(BlueNet_all2a, self).__init__()
        self.l1 = nn.Linear(num_in, num_in*2)
        self.l2 = nn.Linear(num_in*2, num_out*2)
        self.l3 = nn.Linear(num_out*2, num_out)

        self.relu = nn.ReLU()
        self.softmax = nn.Softmax()

    def forward(self, x):
        fc1 = F.relu((self.l1(x)))
        out_x = self.softmax(self.l3(self.relu((self.l2(fc1)))))
        return out_x

class BlueNet_all7(nn.Module):

    def __init__(self, num_in, num_out):
        super(BlueNet_all7, self).__init__()
        self.l1 = nn.Linear(num_in, num_in*2)
        self.l2 = nn.Linear(num_in*2, num_in*4)
        self.l3 = nn.Linear(num_in*4, num_in*8)
        self.l4 = nn.Linear(num_in*8, num_in*4)
        self.l5 = nn.Linear(num_in*4, num_in*2)
        self.l6 = nn.Linear(num_in*2, num_out*4)
        self.l7 = nn.Linear(num_out*4, num_out*2)
        self.l8 = nn.Linear(num_out*2, num_out)

        self.relu = nn.ReLU()
        self.softmax = nn.Softmax()

    def forward(self, x):
        fc1 = F.relu(self.l3(self.l2(self.l1(x))))
        out_x = self.softmax(self.l8(self.l7(self.l6(self.l5(self.l4(fc1))))))
        return out_x

# Model Selection
#models_sel= [BlueNet_all6a(), BlueNet_all4a(), BlueNet_all2a()]
num_in, num_out = train_set0.__inout__()
models_sel= [BlueNet_all7(num_in, num_out), BlueNet_all6a(num_in, num_out), BlueNet_all6b(num_in, num_out), BlueNet_all4a(num_in, num_out), BlueNet_all4b(num_in, num_out), BlueNet_all2a(num_in, num_out)]
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
    scheduler.step()
    model.train()
    acc_result = 0
    for batch_idx, (data, target) in enumerate(train_loader0):
        # reshape to vector
        #data = data.view(data.size(0), -1)
        data = data.type(torch.FloatTensor)
        target = target.type(torch.LongTensor)
        # move to cuda if available
        if IS_CUDA:
            data = data.cuda()
            target = target.cuda()
        # convert to Variable
        data = Variable(data)
        target = Variable(target)
        # forward: evaluate with model
        output = model(data)
        loss = criterion(output, target)
        # backward: compute gradient and update weights
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        # Check accuracy rate
        predict = torch.max(output, 1)[1]
        predict = predict.cpu().data.numpy().squeeze() 
        target = target.cpu().data.numpy()
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
    best_model.eval()
    prediction_list = []
    label_list = []
    for batch_x, y in test_loader0:
        batch_x = batch_x.type(torch.FloatTensor)
        if IS_CUDA:
            batch_x = batch_x.cuda()
        best_loss = 100
        batch_x = Variable(batch_x)
        predict_target = best_model(batch_x)
        predict = torch.max(predict_target, 1)[1]
        predict = predict.cpu().data.numpy().squeeze()
        
        prediction_list.append(predict)
        label_list.append(y)
    return np.concatenate(prediction_list), np.concatenate(label_list)

for model in models_sel:

    if IS_CUDA:
        model.cuda()

    optimizer = optim.Adam(model.parameters(), lr=LR)
    scheduler = optim.lr_scheduler.MultiStepLR(optimizer, [5, 10, 15, 20, 25,30, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100])

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

curve_name = ['7', '6a', '6b', '4a', '4b', '2a']
for i in range(len(training_curve)):
    plt.plot(range(EPOCHS), training_curve[i], label = 'Model{}'.format(curve_name[i]))
plt.legend()
plt.savefig('./result/accuracy_growth.png')
#plt.show()
pred_result = prediction()
style_list = ['Aggressive', 'Conservative' ,'High-hater', 'All-in']
row_list = style_list + ['sum']
confumat = confusion_matrix(pred_result[0], pred_result[1])
margin_sum = np.sum(confumat, axis = 0)
confumat = np.append(confumat, [margin_sum], axis = 0)
confumat = np.divide(confumat.astype(np.float), margin_sum.astype(np.float))
print('Confusion matrix of style prediction')
print(pd.DataFrame(confumat, index = row_list, columns=style_list))
