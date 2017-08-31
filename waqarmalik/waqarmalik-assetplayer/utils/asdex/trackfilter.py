#! /opt/local/bin/python 
'''
 *  Copyright 2013 SESO Group at NASA Ames
 *  Created by Waqar Malik <waqarmalik@gmail.com>
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
'''

import sys
import os.path
import numpy as np

class param:
  z_l = (999, 5000) # z_l ac is on ground, else airborne
  x_l = (-5000, 5000) # x limits of airport rectangle
  y_l = (-5000, 5000) # y limits
  x_s = (-2400, 1400) # airport surface x limits
  y_s = (-1600, 1600) # airport surface y limits
  z_s = (-1, 999) # airport surface z limits
  wsize = 21   # smoothing window size
  d_time = 10  #(sec) catches data with time jump of > and
  d_dist = 100 #(m) ac position jumps by this distance
  v_stop = 1   #
  t_stop = 15  # stop detected if in t sec ac moves less than v*t 
  gate_eps = 10 # (m) is assumed to be at start position
  th_dist = 40 # (m) lookahead for orientation cleaner 

class TrackFilter:
  '''Filters the given track data'''
  def __init__(self, filename):
    self.track_datas = dict() # callsign --> type, arr/dep, state, filtered
    self.read(filename)    
    print('Total number of aircraft: {}'.format(len(self.track_datas)))
    self.clean()
    self.interpolate()
    #self.write_tracks('tracks.txt')
    print('Writing clean interpolated asset/sarda file.')
    fn, ext = os.path.splitext(filename)
    out_file = fn+'_filter'+ext
    self.write_snapshots(out_file)

  def read(self, filename):
    if not os.path.isfile(filename):
      raise(ValueError, filename+' does not exist')
    sim_start_time=-1
    with open(filename) as fn:
      for line in fn:
        line = line.strip().split()
        if len(line)>0 and line[0]!='#':
          sim_time = int(line[0])
          if sim_start_time==-1:
            sim_start_time = float(line[0])
          if int(float(line[0])-sim_start_time) != float(line[0])-sim_start_time:
            print('{0} is in fractional second increment'.format(line[0]))
          utc_time = int(line[1])
          line = fn.readline().strip().split()
          print('Processing snapshot at time: {}'.format(sim_time), end='\r')
          while len(line)!=0:
            call_sign = line[0]
            ac_type = line[1]
            ac_status = line[2]
            state =np.array([float(line[3]), float(line[4]), float(line[5]),
                            float(line[6]), float(line[7]), sim_time, utc_time])
            state.shape = 1,7
            if call_sign in self.track_datas:
              info = self.track_datas[call_sign]
              if info[1]!=ac_status and info[1]=='null':
                info[1]=ac_status
              if info[2][-1,-2] != sim_time:
                info[2] = np.vstack((info[2], state))
              self.track_datas[call_sign] = info
            else:
              self.track_datas[call_sign] = [ ac_type, ac_status, 
                                              state, np.array([]) ]
            line = fn.readline().strip().split()
    print('File read. Track data ends at {}\t\t'.format(sim_time))

  def clean(self):
    for ac in list(self.track_datas.keys()):  #force a copy of keys
      ac_type, ac_status, state, f_state = self.track_datas[ac]
      print('Cleaning {}'.format(ac), end=' ')
      if ac_type=='null' or ac_type=='HELO':
        print('.... {} aircraft type.... removing'.format(ac_type))
        self.track_datas.pop(ac)
        continue
      if np.all(state[:,2] > param.z_l[0]): 
        print('.... always airborne.... removing.')
        self.track_datas.pop(ac)
        continue
      if np.all(state[:,2] < param.z_l[0]): 
        print('.... always on surface.... removing.')
        self.track_datas.pop(ac)
        continue
      if ac_status=='null':
        print('.... has "null" state.')
        #continue;
      state = state[(state[:,0]>param.x_l[0]) & (state[:,0]<param.x_l[1]) &
                    (state[:,1]>param.y_l[0]) & (state[:,1]<param.y_l[1]) &
                    (state[:,2]<param.z_l[1]),:]
      self.track_datas[ac] = [ ac_type, ac_status, state, f_state ]
      if state.size==0:
        print('.... has 0 state size.')
        self.track_datas.pop(ac)
        continue
      diff_state = np.diff(state,axis=0)
      jump_state = diff_state[diff_state[:,-2]>param.d_time,:]
      if np.any(np.sum(jump_state[:,:2]**2, axis=1)>param.d_dist**2):
        print('.... has missing data for > {}sec and distance jump of {}m'.
              format(param.d_time, param.d_dist))
        #print(state[diff_state[:,-2]>param.d_time][:,[0,1,-2]])
      print(' ', end='\r')

  def write_tracks(self, filename):
    with open(filename,'w') as fn:
      for ac in self.track_datas:
        ac_type, ac_status, nstate, fstate = self.track_datas[ac]
        n_state= nstate.copy()
        f_state = fstate.copy()
        n_state = n_state[(n_state[:,0]>param.x_s[0]) & 
                          (n_state[:,0]<param.x_s[1]) &
                          (n_state[:,1]>param.y_s[0]) & 
                          (n_state[:,1]<param.y_s[1]) &
                          (n_state[:,2]>param.z_s[0]) &
                          (n_state[:,2]<param.z_s[1]),:]
        f_state = f_state[(f_state[:,0]>param.x_s[0]) & 
                          (f_state[:,0]<param.x_s[1]) &
                          (f_state[:,1]>param.y_s[0]) & 
                          (f_state[:,1]<param.y_s[1]) &
                          (f_state[:,2]>param.z_s[0]) &
                          (f_state[:,2]<param.z_s[1]),:]

        d_noise = np.concatenate(([0],
                      np.sqrt(np.sum(np.diff(n_state[:,:2],axis=0)**2, axis=1))))
        d_filter = np.concatenate(([0],
                      np.sqrt(np.sum(np.diff(f_state[:,:2],axis=0)**2, axis=1))))
        fn.write('{} {} {}\n'.format(ac, ac_type, ac_status))
        for ind in range(len(n_state)):
          fn.write('{0:.1f}\t{1:.1f}\t{2:.1f}\t{3:.1f}\t{4:.1f}\n'.format(
                                                                n_state[ind,0], 
                                                                n_state[ind,1], 
                                                                n_state[ind,2], 
                                                                n_state[ind,-2],
                                                                d_noise[ind]))
        fn.write('Filetered Data\n')
        for ind in range(len(f_state)):
          fn.write('{0:.1f}\t{1:.1f}\t{2:.1f}\t{3:.1f}\t{4:.1f}\n'.format(
                                                                f_state[ind,0], 
                                                                f_state[ind,1], 
                                                                f_state[ind,2], 
                                                                f_state[ind,-2],
                                                                d_filter[ind]))
        fn.write('\n\n')

  def write_snapshots(self,filename):
    map_time = dict()
    snapshots = dict()
    num=0
    for ac in self.track_datas:
      print('{}......{}'.format(num,ac), end='\r')
      num +=1
      ac_type, ac_status, n_state, f_state = self.track_datas[ac]
      # [time] --> utc [ac type status x y z O v]
      f_state = f_state
      for ind in range(len(f_state)):
        key = '{0:.0f}'.format(f_state[ind,-2])
        if key not in map_time:
          map_time[key] = '{0:.0f}'.format(f_state[ind,-1])
        if key not in snapshots:
          snapshots[key] = [ [ac,ac_type,ac_status] + list(f_state[ind,:5]) ]
        else:
          snapshots[key] = snapshots[key] + [ [ac,ac_type,ac_status]+ 
                                                       list(f_state[ind,:5]) ]
    with open(filename, 'w') as fn:
      time = sorted(map_time.keys(), key=float)
      for ind, t in enumerate(time):
        if ind>0 and float(time[ind])>float(time[ind-1])+1:
          for x in np.arange(float(time[ind-1])+1, float(time[ind])):
            t_tmp = '{0:.0f}'.format(x)
            utc_tmp = '{0:.0f}'.format(float(map_time[time[ind-1]])+x-float(time[ind-1]))
            fn.write('{}\t{}\t{}\n\n'.format(t_tmp, utc_tmp, 0))
          fn.write('{}\t{}\t{}\n'.format(t, map_time[t], len(snapshots[t])))
          for i in snapshots[t]:
            fn.write('{0[0]} {0[1]} {0[2]} {0[3]:.1f} {0[4]:.1f} '
                     '{0[5]:.1f} {0[6]:.0f} {0[7]:.1f}\n'.format(i) )
          fn.write('\n')
        else:
          fn.write('{}\t{}\t{}\n'.format(t, map_time[t], len(snapshots[t])))
          for i in snapshots[t]:
            fn.write('{0[0]} {0[1]} {0[2]} {0[3]:.1f} {0[4]:.1f} '
                     '{0[5]:.1f} {0[6]:.0f} {0[7]:.1f}\n'.format(i) )
          fn.write('\n')
      

  def interpolate(self):
    for ac in self.track_datas:
      ac_type, ac_status, n_state, f_state = self.track_datas[ac]
      state = n_state.copy()
      state = self.stop_cleaner(state)
      f_state = np.zeros( (state[-1,-2]-state[0,-2]+1,7) )
      f_state[-1,:] = state[-1,:]
      f_ind=0;
      print('Interpolating tracks for {0}    '.format(ac), end='\r')
      for ind in range(len(state)-1):
        if state[ind-1,-2]==state[ind,-2]:
          print('WHY THIS WHY THIS?')
        if state[ind,-2]==state[ind+1,-2]:
          print('WHY THIS WHY THIS = ')
        if state[ind+1,-2]==state[ind,-2]+1:
          f_state[f_ind,:] = state[ind,:]
          f_ind = f_ind+1;
        elif state[ind+1,-2]>state[ind,-2]+1:
          missing = np.linspace(0,1, state[ind+1,-2]-state[ind,-2]+1)
          missing = missing[:-1]
          for x in missing:
            f_state[f_ind,:] = (1-x)*state[ind,:] + x*state[ind+1,:]
            f_ind = f_ind+1;
        else:
          print('Cannot interpolate for {}'.format(ac))
          raise(ValueError,'Kolaveri')
      f_state = f_state.copy()
      # track data smoothing 
      for i in range(5):
        if(len(f_state) >= param.wsize):
          f_state[:,i] = self.smooth(f_state[:,i], window_len=param.wsize, 
                                     window='hamming')
      # orientation and speed derived
      f_state = self.orientation_cleaner(f_state)
      self.track_datas[ac] = [ac_type, ac_status, n_state, f_state]
    print(' '*100)

  def stop_cleaner(self, state):
    i=0
    while i < len(state)-1:
      j = i
      while i<len(state)-1 and state[i+1,-2]-state[j,-2] < param.t_stop:
        i+=1
      i = i+1 if i!=len(state)-1 else i
      diff_state = np.diff(state[[j,i],:],axis=0)
      if np.sum(diff_state[0,:2]**2) < (diff_state[0,-2]*param.v_stop)**2:
        print('*', end='\r')
        for ind in range(j,i):
          state[ind,:-2] = state[j,:-2]
      i = j+1
    
    stop=0
    if state[0,2]<1000: # departure.
      for i in range(1,len(state)):
        diff_state = np.diff(state[[0,i],:],axis=0)
        if np.sum(diff_state[0,:2]**2) < param.gate_eps**2:
          stop = i
          print('-', end='\r')
    if stop>0:
      for ind in range(stop):
        state[ind,:-2] = state[0,:-2]

    stop=0
    if state[-1,2]<1000: # arrival.
      for i in range(len(state)-1,0,-1):
        diff_state = np.diff(state[[i,-1],:],axis=0)
        if np.sum(diff_state[0,:2]**2) < param.gate_eps**2:
          stop = i
          print('-', end='\r')
    if stop>0:
      for ind in range(stop,len(state)):
        state[ind,:-2] = state[-1,:-2]

    return(state)

  def orientation_cleaner(self, f_state):
      diff_state = np.diff(f_state, axis=0)
      speed = np.sqrt(np.sum(diff_state[:,:2]**2, axis=1))
      speed = np.vstack( (speed.reshape(-1,1), [speed[-1]]) ) 
      dist=np.cumsum(speed)
      j=1
      theta=[]
      for i in range(len(speed)-1):
        while dist[j]-dist[i] < param.th_dist and j<len(speed)-1:
          j = j+1
        theta = theta + [np.arctan2(f_state[j,0]-f_state[i,0], 
                                    f_state[j,1]-f_state[i,1]) * 180/np.pi]
      theta = theta + [theta[-1]]
      for i in range(len(theta)-1):
        if i>0 and abs(diff_state[i,0])<1e-2 and abs(diff_state[i,1])<1e-2:
          theta[i] = theta[i-1]
        j=i+1
        if theta[i] < theta[j]:
          while theta[j]-theta[i] > 180:
            theta[j] -= 360
        elif theta[i] > theta[j]:
          while theta[i]-theta[j] > 180:
            theta[j] += 360
      #theta = self.smooth(theta.reshape(-1), window_len=11, window='hanning')
      f_state[:,3] = theta
      f_state[:,4] = speed.reshape(-1)
      
      return(f_state)


  def smooth(self, x,window_len=11, window='hanning'):
    '''smooth the data using a window with requested size.'''
    if x.ndim != 1:
      raise(ValueError, "smooth only accepts 1 dimension arrays.")
    if x.size < window_len:
      raise(ValueError, "Input vector needs to be bigger than window size.")
    if window_len<3:
      return x
    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
      raise(ValueError, "window = flat, hanning, hamming, bartlett, blackman")
    s=np.r_[x[window_len-1::-1],x,x[-1:-window_len:-1]]
    if window == 'flat': #moving average
      w=np.ones(window_len,'d')
    else:
      w=eval('np.'+window+'(window_len)')
    y=np.convolve(w/w.sum(),s,mode='same')
    y_filter = y[window_len: -window_len+1]
    if len(x)!=len(y_filter):
      raise(ValueError, 'size mismatch')
    return y_filter 

if __name__ == '__main__':
  filename = sys.argv[1]
  my_track = TrackFilter(filename)
  print('Total number of aircraft: {}'.format(len(my_track.track_datas)))

  

