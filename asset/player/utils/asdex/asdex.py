#!/opt/local/bin/python

import sys, os
import numpy as np
import pickle
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.lines import Line2D

import trackfilter as tf

class TrackViewer:
  def __init__(self, filename, ac=None):
    if not os.path.isfile(filename):
      raise ValueError(filename + ' does not exist')
    fn, ext = os.path.splitext(filename)
    if ext=='.sarda':
      self.my_track = tf.TrackFilter(filename).track_datas
      dat_file = fn+'.pickle'
      f = open(dat_file, 'wb')
      pickle.dump(self.my_track, f, pickle.HIGHEST_PROTOCOL)
      f.close()
    elif ext=='.pickle':
      f = open(filename, 'rb')
      self.my_track = pickle.load(f)
      f.close()
    print('Total number of aircraft: {}'.format(len(self.my_track)))
    self.acList = list(self.my_track.keys())
    self.ind = 0 if ac==None else self.acList.index(ac)
    self.draw()

  def press(self, event):
    if event.key==',' or event.key=='<':
      self.ind = self.ind-1
    if event.key=='.' or event.key=='>':
      self.ind = self.ind+1
      if self.ind>=len(self.acList):
        self.ind=0
    ac = self.acList[self.ind]
    ac_type, ac_status, n_state, f_state = self.my_track[ac]
    self.n_data.set_data(n_state[:,0], n_state[:,1])
    self.f_data.set_data(f_state[:,0], f_state[:,1])
    ac_txt = '{0}\n{1}\n{2} ({3})'.format(ac, ac_type, ac_status, self.ind)
    self.ac_stat.set_text(ac_txt)
    plt.draw()

  def draw(self):
    fig = plt.figure()
    fig.canvas.set_window_title('Track Viewer')
    fig.canvas.mpl_connect('key_press_event', self.press)
    ax = fig.add_axes([0,0,1,1])
    self.draw_map(ax)
    self.n_data = Line2D([], [], color='red', marker='.', ls='--', lw=1)
    self.f_data = Line2D([], [], color='cyan', linewidth=1)
    ax.add_line(self.n_data)
    ax.add_line(self.f_data)
    ac = self.acList[self.ind]
    ac_type, ac_status, n_state, f_state = self.my_track[ac]
    self.n_data.set_data(n_state[:,0], n_state[:,1])
    self.f_data.set_data(f_state[:,0], f_state[:,1])
    ac_txt = '{0}\n{1}\n{2} ({3})'.format(ac, ac_type, ac_status, self.ind)
    props = dict(boxstyle='round', facecolor='gray', alpha=0.6)
    self.ac_stat = ax.text(10, 50, ac_txt, 
                           transform=None, fontsize=12, verticalalignment='top',
                           bbox=props)
    ax.autoscale_view()
    ax.set_xticks([]), ax.set_yticks([]) 
    plt.axis('equal')
    plt.show()

  def draw_map(self, ax):
    if not os.path.isfile('../data/KCLT/kclt.quad'):
      raise(ValueError, 'Quad file does not exist')
    with open('../data/KCLT/kclt.quad') as fn:
      poly_col = []
      x = []
      y = []
      for line in fn:
        xv,yv,r,g,b = [ float(i) for i in line.split() ]
        vert_col = (r,g,b)
        if len(poly_col)>0 and vert_col != poly_col:
          polys=[]
          for i in range(0,len(x),4):
            polys.append(list(zip(x[i:i+4],y[i:i+4])))
          ax.add_collection(PolyCollection( polys, facecolors=poly_col, 
                                          edgecolors=poly_col, linewidths=1 ))
          x = []
          y = []
        x = x + [xv+626.9468]
        y = y + [yv+1204.979]
        poly_col = vert_col


if __name__ =='__main__':
  if len(sys.argv)==2:
    TrackViewer(sys.argv[1])
  elif len(sys.argv)==3:
    TrackViewer(sys.argv[1], sys.argv[2])
  else:
    raise ValueError('Usage: displayTrack.py <trackFile> <optional:aircraftID>')

