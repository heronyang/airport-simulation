/**
 *  Copyright (c) 2014  Waqar Malik <waqarmalik@gmail.com>
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
 */

#ifndef STATES_HPP
#define STATES_HPP

#include <string>
#include <vector>
#include <utility>
#include <unordered_map>

/**
 * @brief The State struct
 * An aircraft in simulation (surface or air) has a state defined through the
 * 'State' struct. At any time, 'time' (w.r.t some reference) the aircraft is
 * described by its position 'x', 'y', 'z' (m)(from the origin at airport),
 * it's orientation 'head' (degrees) and the speed. It also contains a boolean
 * specifying whether the aircraft is in conflict.
 */
struct State {
  // defines the location, heading, speed at given elapsed time.
  double x;
  double y;
  double z;
  double head;
  double speed;
  double time;
  std::string status;
  bool conflict = false;
};

/**
 * @brief The Scenario class
 * This class loads the complete simulation/track_information from *.asset file.
 * The data is loaded as a snapshot of the surface at each time. It provides
 * accessor function to get the current snapshot that is tracked by an iterator.
 * It also provides accessor function to access the aircraft model type and
 * status (arrival/departure), and its complete track given the call_sign.
 */
class Scenario {
public:
  // trackFile is the "asset" file containing the track information.
  Scenario(const std::string &trackFile, bool doConflict);
  void toStdOut();
  void outSnapshot(std::pair<double, std::unordered_map<std::string, State>> &);

  double getSimStartTime();
  long getUtcStartTime();
  double getSimLength();

  double setIterator(double percent, std::unordered_map<std::string, State> &);
  double getSnapshot(double step, std::unordered_map<std::string, State> &);
  std::vector<std::pair<std::string, std::string>> getConflicts();
  std::string getAircraftType(const std::string &);
  bool getAircraftStatus(const std::string &);
  std::vector<State> getAircraftTrack(const std::string &);

protected:
  void readTracks(const std::string &);
  void readAircraftSize(const std::string &);

private:
  // mAircraftTypeList: callsign -> (model type, bool isDeparture)
  // E.g. mAircraftTypeList['AWE1031'] returns a pair {"A310", True}
  std::unordered_map<std::string, std::pair<std::string, bool>> mAircraftTypeList;

  // mAircraftSize: callsign -> (length, wingspan)
  std::unordered_map<std::string, std::pair<double, double>> mAircraftSize;

  // mSnapshots: vector --> <time, (callsign, State)>
  // e.g. mSnapshots[14] returns pair < 14, {"AWE930":x,y,z,phi,v;
  // "AAL20":x,y,z,phi,v} >
  std::vector<std::pair<double, std::unordered_map<std::string, State>>> mSnapshots;

  // mTrackDatas["AWE1031"] return a vector of States
  std::unordered_map<std::string, std::vector<State>> mTrackDatas;

  // mSnapshots is a vector. mCurrentSnapshotIterator is the iterator to
  // mSnapshots. When the scneario class is asked to provide a snapshot,
  // it returns the value corrsponding to mCurrentSnapshotIterator,
  // and updates the iterator accordingly.
  std::vector<std::pair<double, std::unordered_map<std::string, State>>>::iterator mCurrentSnapshotIterator;

  bool mDoConflict;
  // mConflictMap stores the conflict that occurs at any given time. The key is
  // a double indicating a time and the value corresponds to a vector of pair
  // of aircraft that are at conflict at the given time
  std::unordered_map<double, std::vector<std::pair<std::string, std::string>>> mConflictMap;

  // For a given surface snapshot, find the pairs of aircraft in conflict.
  std::vector<std::pair<std::string, std::string>> findConflicts(std::unordered_map<std::string, State> &);
  bool inConflict(std::unordered_map<std::string, State>::iterator,
                  std::unordered_map<std::string, State>::iterator);

  // the scneario class also interpolates between the 1 second track information
  // when it provides snapshots to caller. mMinistep is used in the
  // interpolation.
  // It stores the value of how much has been interpolated between current and
  // next interator.
  double mMinistep = 0;

  long mUtcStartTime = -1;   // track start time in UTC.
  double mSimStartTime = -1; // track start time.
  double mSimLength = -1;    // final track end time
};

#endif // STATES_HPP
