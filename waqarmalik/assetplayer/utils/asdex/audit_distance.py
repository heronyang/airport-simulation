#!/opt/local/bin/python

import sys, os
import pickle
import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt

def make_plot(dist_error):
  fig = plt.figure();
  ax1 = fig.add_subplot(111)
  ax1.yaxis.grid(True, linestyle='-', which='major', color='w', alpha=1.0)
  ax1.patch.set_facecolor('0.90')
  ax1.set_axisbelow(True)
  ax1.hist(dist_error,bins=100, color='b', alpha=0.6)
  ax1.set_title("Percent difference in calculated distances")
  ax1.set_xlabel("Percent")
  ax1.set_ylabel("Count")
  
  ax2 = fig.add_axes([0.7,0.3,.15,.5])
  ax2.yaxis.grid(True, linestyle='-', which='major', color='lightblue', alpha=1.0)
  ax2.patch.set_facecolor('0.95')
  ax2.set_axisbelow(True)
  bp = ax2.boxplot(dist_error, notch=0, sym='+', vert=1, whis=1.5)
  plt.setp(bp['boxes'], color='black')
  plt.setp(bp['whiskers'], color='black')
  plt.setp(bp['fliers'], color='blue', marker='None')
  plt.setp(bp['medians'], color='black')
  ax2.set_title('Statistics', fontsize=11)
  ax2.set_xticks([])
  plt.setp(ax2.get_yticklabels(), rotation='horizontal', fontsize=9)
  ax2.set_ylabel('Value (%)', fontsize=11)
  ax2.set_ylim([-5,50])
  #ax2.margins(None, 0.02)
  ax2.scatter([1],np.mean(dist_error))
  
  plt.show()

def get_states(ac):
  x_s = (-2400, 1400) # airport surface x limits
  y_s = (-1600, 1600) # airport surface y limits
  z_s = (-1, 999) # airport surface z limits
  ac_type, ac_status, n_state, f_state = tracks[ac]
  n_state = n_state[(n_state[:,0]> x_s[0]) & (n_state[:,0]< x_s[1]) &
                    (n_state[:,1]> y_s[0]) & (n_state[:,1]< y_s[1]) &
                    (n_state[:,2]> z_s[0]) & (n_state[:,2]< z_s[1]),:]
  f_state = f_state[(f_state[:,0]> x_s[0]) & (f_state[:,0]< x_s[1]) &
                    (f_state[:,1]> y_s[0]) & (f_state[:,1]< y_s[1]) &
                    (f_state[:,2]> z_s[0]) &(f_state[:,2]< z_s[1]),:]
  a = np.sqrt(np.sum(np.diff(f_state[:,:2], axis=0)**2, axis=1))
  f_state[:,3] = np.concatenate(([0],np.cumsum(a)))
  a = np.sqrt(np.sum(np.diff(n_state[:,:2], axis=0)**2, axis=1))
  n_state[:,3] = np.concatenate(([0],np.cumsum(a)))
  return n_state, f_state

if __name__ == '__main__':
  if len(sys.argv)<2:
    raise ValueError('Usage: ./audit_distance.py <pickle>')
  filename = sys.argv[1]
  f = open(filename, 'rb')
  tracks = pickle.load(f)
  f.close()
  print('Processing data:')
  debug =True if len(sys.argv)==3 else False
  if debug and sys.argv[2] in tracks:
    callsign = sys.argv[2]
    n_state,f_state = get_states(callsign)
    print('{}'.format(callsign))
    for i in range(len(f_state)):
      nstate = n_state[ n_state[:,-2]==f_state[i,-2],:] 
      if len(nstate) == 0:
        nstate = [[-1]*7]
      print('{0[5]:10.0f} ({1[0]:7.1f},{1[1]:7.1f})   N{1[3]:8.1f}\t'
            '({0[0]:7.1f},{0[1]:7.1f})   F{0[3]:8.1f}'''.format(
                                                    f_state[i,:], nstate[0] ))
  else:
    dist_error = []
    for ac in tracks.keys():
      n_state,f_state = get_states(ac)
      f_dist = f_state[-1,3]
      n_dist = n_state[-1,3]
      d_err = (n_dist-f_dist)*100/f_dist
      if debug:
        if n_state[0,-2]!=f_state[0,-2] or n_state[-1,-2]!=f_state[-1,-2]:
          print('{}: N({},{}) F({},{})'.format(ac, n_state[0,-2], f_state[0,-2],
                                                n_state[-1,-2], f_state[-1,-2]))
      else:
        if d_err<0 or d_err>100:
          print('\t{0} ({1:.1f})'.format(ac,d_err))
        else:
          dist_error += [d_err]

    if not debug:
      make_plot(dist_error)

    print(sum(dist_error)/len(dist_error))
