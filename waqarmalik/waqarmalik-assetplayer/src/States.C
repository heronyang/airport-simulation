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

#include <cassert>
#include <fstream>
#include <sstream>
#include <iostream>
#include <array>
#include <cmath>
#include <functional>
#include <algorithm>

#include "States.H"

Scenario::Scenario(const std::string &trackFile, bool doConflict) {
  mDoConflict = doConflict;
  readAircraftSize("data/images/aircraft_texture_size.txt");
  readTracks(trackFile);
  mCurrentSnapshotIterator = mSnapshots.begin();

  if (mDoConflict) {
    std::ofstream out("conflicts.out");
    assert(out);
    for (auto &cmap : mConflictMap) {
      out << "\nTime: " << cmap.first << "\n";
      for (auto &pair : cmap.second)
        out << pair.first << " " << pair.second << "\n";
    }
    out.close();
  }
}

/**
 * @brief Scenario::readTracks
 * @param trackFile: asset file containing the track information.
 */
void Scenario::readTracks(const std::string &trackFile) {
  std::ifstream inFile(trackFile);
  assert(inFile);

  double simTime;
  double prevTime = -1;
  long utcTime;
  std::string line, tmp;
  std::stringstream ss;

  std::string callSign, acType;
  bool isDep;
  std::unordered_map<std::string, State> snapshot;

  int ind = 0;
  std::string progress = "-\\|/";
  while (getline(inFile, line)) {
    int x = ind % 4;
    std::cout << "Processing tracks: " << ++ind << " " << progress[x] << "\r";
    std::cout.flush();
    if (line.size() > 0 && line[line.size() - 1] == '\r')
      line.resize(line.size() - 1);
    while (!line.empty() && *line.begin() == ' ')
      line.erase(line.begin());
    if (!line.empty() && line.size() > 0 && line[0] != '#') {
      // Line is NOT empty, blank spaces only, or a comment '#'
      State tmpState;
      ss << line;
      ss >> simTime >> utcTime >> callSign >> acType >> tmp >> tmpState.status >> tmpState.x >> tmpState.y >>
          tmpState.z >> tmpState.head >> tmpState.speed;
      if (mSimStartTime == -1) {
        mSimStartTime = simTime;
        mUtcStartTime = utcTime;
        prevTime = simTime;
      }
      if (prevTime != simTime) { // a new time, hence storing the prev snapshot
        if (mDoConflict)
          mConflictMap[prevTime - mSimStartTime] = findConflicts(snapshot);
        mSnapshots.push_back(std::make_pair(prevTime - mSimStartTime, snapshot));
        snapshot.clear();
        prevTime = simTime;
      }
      tmpState.time = simTime - mSimStartTime;
      if (tmpState.status == "VEC" ||
          (tmpState.status.length() >= 3 && tmpState.status.substr(tmpState.status.length() - 3) == "DEP"))
        isDep = true;
      else
        isDep = false;
      if (tmpState.status == "null")
        std::cout << callSign << " has 'null' status at " << simTime << std::endl;
      // Update mAircraftTypeList
      if (mAircraftTypeList.count(callSign) == 0)
        mAircraftTypeList[callSign] = std::make_pair(acType, isDep);
      else {
        if (mAircraftTypeList[callSign].first != acType) {
          std::cout << "Mismatch in type for " << callSign << " at " << simTime << ". (was "
                    << mAircraftTypeList[callSign].first << " and now " << acType << ")" << std::endl;
        }
        if (mAircraftTypeList[callSign].second != isDep)
          if (!(mAircraftTypeList[callSign].second && tmpState.status == "ONRTE")) {
            // Not a former departure that changed to arrival for another
            // destination
            std::cout << "Mismatch in status for " << callSign << " at " << simTime
                      << " (was dep=" << mAircraftTypeList[callSign].second << "->" << isDep
                      << " current status:" << tmpState.status << ")" << std::endl;
            mAircraftTypeList[callSign].second = isDep;
          }
      }
      // Update snapshot
      if (snapshot.count(callSign) == 0)
        snapshot[callSign] = tmpState;
      else {
        if (snapshot[callSign].x != tmpState.x || snapshot[callSign].y != tmpState.y ||
            snapshot[callSign].z != tmpState.z || snapshot[callSign].head != tmpState.head ||
            snapshot[callSign].speed != tmpState.speed)
          std::cout << callSign << ": multiple entries at " << simTime << std::endl;
      }
      mTrackDatas[callSign].push_back(tmpState);

      while (ss >> tmp) {
      };
      ss.str("");
      ss.clear();
      line = "";
    }
  }
  mSimLength = mSnapshots.back().first;

  prevTime = -1;
  for (auto snapshot : mSnapshots) {
    if (snapshot.first != prevTime + 1)
      std::cout << "(WWW) Snapshot missed at " << mSimStartTime + prevTime + 1 << std::endl;
    prevTime = snapshot.first;
  }
  std::cout << "Processed Tracks";
  for (int i = 0; i < 80; ++i)
    std::cout << " ";
  std::cout << "\nScenario is " << int(mSimLength / 3600) << " hours, " << int(mSimLength / 60) % 60
            << " minutes long." << std::endl;
  std::cout << mAircraftTypeList.size() << " aircraft tracked." << std::endl;
}

/**
 * @brief Scenario::readAircraftSize
 * @param filename
 * Reads the aircraft length and width used to determine conflict.
 */
void Scenario::readAircraftSize(const std::string &filename) {
  std::ifstream inFile(filename);
  assert(inFile);
  std::string line, tmp, model, texture_file;
  std::stringstream ss;
  double length, wingspan;
  while (getline(inFile, line)) {
    if (line.size() > 0 && line[line.size() - 1] == '\r')
      line.resize(line.size() - 1);
    while (!line.empty() && *line.begin() == ' ')
      line.erase(line.begin());
    if (!line.empty() && line.size() > 0 && line[0] != '#') {
      ss << line;
      ss >> model >> texture_file >> length >> wingspan;
      mAircraftSize[model] = std::make_pair(length, wingspan);
    }
    while (ss >> tmp) {
    };
    ss.str("");
    ss.clear();
    line = "";
  }
}

/**
 * @brief Scenario::setIterator Sets value of mCurrentSnapshotIterator
 * @param percent - Sets iterator to this percentage of size of mSnapshots
 * @param snapshot - returns the snapshot at the given percent
 * @return the 'time' of the snapshot.
 */
double Scenario::setIterator(double percent, std::unordered_map<std::string, State> &snapshot) {
  int move = int(percent * mSnapshots.size() / 100);
  mCurrentSnapshotIterator = mSnapshots.begin() + move;
  if (mCurrentSnapshotIterator == mSnapshots.end()) {
    snapshot = mSnapshots.back().second;
    return (mSnapshots.back().first);
  }
  snapshot = (*mCurrentSnapshotIterator).second;
  return ((*mCurrentSnapshotIterator).first);
}

/**
 * @brief Scenario::getSnapshot Get value pointed to by mCurrentSnapshotIterator
 * @param step -
 * @param snapshot - returns the snapshot in this variable.
 * @return the 'time' of the returned snapshot
 *
 * Asuumes that track snapshots are at 1Hz. The 'step' is then fraction of s
 * seconds the snapshot is asked for. If the playback rate is high (~30x) and
 * FPS of display is 20 (for smooth playback) then step will be 1.5. This means
 * that we have to go to next iterator as current iterator, and then interpolate
 * by .5. The variable mMinistep stores any fraction we were in teh last call to
 * this fraction and makes sure we start counting from there.
 */
double Scenario::getSnapshot(double step, std::unordered_map<std::string, State> &snapshot) {
  snapshot.clear();
  if (step > 0 && mCurrentSnapshotIterator == mSnapshots.end()) {
    snapshot = mSnapshots.back().second;
    return (mSnapshots.back().first);
  }
  if (step < 0 && mCurrentSnapshotIterator == mSnapshots.begin()) {
    snapshot = mSnapshots.front().second;
    return (mSnapshots.front().first);
  }
  while (step >= 1) {
    step -= 1;
    ++mCurrentSnapshotIterator;
    if (mCurrentSnapshotIterator == mSnapshots.end()) {
      snapshot = mSnapshots.back().second;
      return (mSnapshots.back().first);
    }
  }
  while (step <= -1) {
    step += 1;
    --mCurrentSnapshotIterator;
    if (mCurrentSnapshotIterator == mSnapshots.begin()) {
      snapshot = mSnapshots.front().second;
      return (mSnapshots.front().first);
    }
  }
  mMinistep = mMinistep + step;
  if (mMinistep >= 1) {
    mMinistep -= 1;
    ++mCurrentSnapshotIterator;
    if (mCurrentSnapshotIterator == mSnapshots.end()) {
      snapshot = mSnapshots.back().second;
      return (mSnapshots.back().first);
    }
  }
  if (mMinistep < 0) {
    mMinistep += 1;
    --mCurrentSnapshotIterator;
  }
  auto nit = mCurrentSnapshotIterator + 1;
  if (mMinistep == 0 || nit == mSnapshots.end()) {
    snapshot = (*mCurrentSnapshotIterator).second;
    return ((*mCurrentSnapshotIterator).first);
  } else {
    State tmpState;
    for (auto ac : (*mCurrentSnapshotIterator).second) {
      if ((*nit).second.count(ac.first) == 0) {
        // Can't be dropped, since this aircraft could be in conflict list.
        // That can make the AssetPlayer crash in drawConflicts().
        tmpState = ac.second;
        tmpState.time = (1 - mMinistep) * ac.second.time + mMinistep * (*nit).first;
        snapshot[ac.first] = tmpState;
      } else {
        tmpState.status = ac.second.status;
        tmpState.conflict = ac.second.conflict;
        tmpState.x = (1 - mMinistep) * ac.second.x + mMinistep * (*nit).second[ac.first].x;
        tmpState.y = (1 - mMinistep) * ac.second.y + mMinistep * (*nit).second[ac.first].y;
        tmpState.z = (1 - mMinistep) * ac.second.z + mMinistep * (*nit).second[ac.first].z;
        // prevent heading jump when crossing 0/360. for values of 359 and 1,
        // the aircraft has rotated by 2 deg and not by 358.
        double a = ac.second.head;
        double b = (*nit).second[ac.first].head;
        a = (a < b && a + 180 - b < 0) ? a + 360 : a;
        b = (b < a && b + 180 - a < 0) ? b + 360 : b;
        tmpState.head = (1 - mMinistep) * a + mMinistep * b;
        tmpState.speed = (1 - mMinistep) * ac.second.speed + mMinistep * (*nit).second[ac.first].speed;
        tmpState.time = (1 - mMinistep) * ac.second.time + mMinistep * (*nit).second[ac.first].time;
        snapshot[ac.first] = tmpState;
      }
    }
    return (tmpState.time);
  }
}

double Scenario::getSimStartTime() { return mSimStartTime; }

long Scenario::getUtcStartTime() { return mUtcStartTime; }

double Scenario::getSimLength() { return mSimLength; }

std::vector<State> Scenario::getAircraftTrack(const std::string &callsign) {
  if (mTrackDatas.count(callsign) == 0) {
    std::cout << "(get_track): " << callsign << " not found in database." << std::endl;
    return (std::vector<State>());
  }
  return mTrackDatas[callsign];
}

/**
 * @brief Scenario::getAircraftType
 * @param callsign
 * @return the model of the aircraft.
 */
std::string Scenario::getAircraftType(const std::string &callsign) {
  if (mAircraftTypeList.count(callsign) == 0) {
    std::cout << "(get_type): " << callsign << " not found in database." << std::endl;
    return ("");
  }
  return mAircraftTypeList[callsign].first;
}

/**
 * @brief Scenario::getAircraftStatus
 * @param callsign
 * @return bool indication whether aircraft is departure (true) or arrival
 */
bool Scenario::getAircraftStatus(const std::string &callsign) {
  if (mAircraftTypeList.count(callsign) == 0) {
    std::cout << "(get_status): " << callsign << " not found in database." << std::endl;
    return (false);
  }
  return mAircraftTypeList[callsign].second;
}

void Scenario::toStdOut() {
  for (auto snapshot : mSnapshots) {
    outSnapshot(snapshot);
  }

  for (auto ac : mTrackDatas) {
    int tprev = 0;
    for (auto acTrack : ac.second) {
      if (tprev != 0) {
        if (acTrack.time - tprev > 1)
          std::cout << ac.first << " track skipped: " << tprev << " - " << acTrack.time << std::endl;
      }
      tprev = acTrack.time;
    }
  }
  std::cout << "Number of aircraft: " << mTrackDatas.size() << std::endl;
}

void Scenario::outSnapshot(std::pair<double, std::unordered_map<std::string, State>> &snapshot) {
  std::cout << snapshot.first + mSimStartTime << " " << snapshot.second.size() - 1 << std::endl;
  for (auto ac : snapshot.second) {
    std::cout << ac.first << " " << mAircraftTypeList[ac.first].first << " "
              << mAircraftTypeList[ac.first].second << " " << ac.second.x << " " << ac.second.y << std::endl;
  }
  std::cout << std::endl;
}

/**
 * @brief Scenario::findConflicts
 * @param snapshot
 * @return Iterate through the current snapshot and compare each aircraft with
 * all other aircraft and check whether they are in conflict.
 */
std::vector<std::pair<std::string, std::string>>
Scenario::findConflicts(std::unordered_map<std::string, State> &snapshot) {
  std::vector<std::pair<std::string, std::string>> conflicts;
  auto it2 = snapshot.begin();
  for (auto it1 = snapshot.begin(); it1 != snapshot.end(); ++it1) {
    if (it1->second.status.compare(0, 4, "GATE") == 0)
      continue;
    it2 = it1;
    ++it2;
    for (; it2 != snapshot.end(); ++it2) {
      if (it2->second.status.compare(0, 4, "GATE") == 0)
        continue;
      if (inConflict(it1, it2)) {
        it1->second.conflict = true;
        it2->second.conflict = true;
        conflicts.push_back(std::make_pair(it1->first, it2->first));
        // Reverse fill values, so that it looks like predicted CDR.
        // If at previous time, ac1 and ac2 were not in conflict, then fill
        // last XXX seconds as being in conflicts.
        double past = 20;
        double fromTime = it1->second.time - past; // conflict from this time.
        // current snapshot has not been put in mSnapshots
        for (auto rit = mSnapshots.rbegin(); rit != mSnapshots.rend(); ++rit) {
          if (rit->first > fromTime && rit->second.count(it1->first) > 0 &&
              rit->second.count(it2->first) > 0) {
            if (rit->second.at(it1->first).conflict && rit->second.at(it2->first).conflict) {
              break;
            } else {
              mConflictMap[rit->first].push_back(std::make_pair(it1->first, it2->first));
            }
          }
        }
      }
    }
  }
  return conflicts;
}

/**
 * @brief Scenario::inConflict
 * @param it1
 * @param it2
 * @return Given two aircraft, return true if they are in conflict.
 */
bool Scenario::inConflict(std::unordered_map<std::string, State>::iterator it1,
                          std::unordered_map<std::string, State>::iterator it2) {
  std::string model1 = this->getAircraftType(it1->first);
  std::string model2 = this->getAircraftType(it2->first);
  if (mAircraftSize.count(model1) == 0)
    model1 = "default";
  if (mAircraftSize.count(model2) == 0)
    model2 = "default";
  double l1 = mAircraftSize[model1].first;
  double l2 = mAircraftSize[model2].first;
  double x1 = it1->second.x, y1 = it1->second.y;
  double x2 = it2->second.x, y2 = it2->second.y;
  // if aircraft are separated by distance greater than sum of their length,
  // then there is no chance of collision
  if (std::pow(x1 - x2, 2) + std::pow(y1 - y2, 2) > std::pow(l1 + l2, 2))
    return false;
  // Else check for conflicting aircraft rectangle.
  /*
   * If two convex polygon are not in collision, there is a separating axis.
   * In essence, there exists an axis perpendicular to an edge of one of the
   * polygons that has no overlap between the projected vertices of the two
   * polygons. We project the vertices of the two polygons that we are testing
   * onto each axis that is perpendicular to the edges of each polygon.
   * If any axis shows no overlap then a collision is impossible.
  */
  l1 = l1 / 2;
  l2 = l2 / 2;
  // Scaling factor for front half of aircraft. Also in AssetPlayer::drawBbox
  // At higher speed we look at longer rectangle.
  double ls1 = 0.5 / (0.5 - std::min(0.3, it1->second.speed / 30));
  double ls2 = 0.5 / (0.5 - std::min(0.3, it2->second.speed / 30));
  double w1 = mAircraftSize[model1].second / 2;
  double w2 = mAircraftSize[model2].second / 2;
  double pi = 4 * std::atan(1);
  double t1 = (90 - it1->second.head) * pi / 180;
  double t2 = (90 - it2->second.head) * pi / 180;
  double ct1 = std::cos(t1), st1 = std::sin(t1);
  double ct2 = std::cos(t2), st2 = std::sin(t2);
  std::array<std::array<double, 2>, 4> vertex1 = {
      {{{x1 + ls1 * l1 * ct1 + w1 * st1, y1 + ls1 * l1 * st1 - w1 * ct1}},
       {{x1 + ls1 * l1 * ct1 - w1 * st1, y1 + ls1 * l1 * st1 + w1 * ct1}},
       {{x1 - l1 * ct1 - w1 * st1, y1 - l1 * st1 + w1 * ct1}},
       {{x1 - l1 * ct1 + w1 * st1, y1 - l1 * st1 - w1 * ct1}}}};
  std::array<std::array<double, 2>, 4> vertex2 = {
      {{{x2 + ls2 * l2 * ct2 + w2 * st2, y2 + ls2 * l2 * st2 - w2 * ct2}},
       {{x2 + ls2 * l2 * ct2 - w2 * st2, y2 + ls2 * l2 * st2 + w2 * ct2}},
       {{x2 - l2 * ct2 - w2 * st2, y2 - l2 * st2 + w2 * ct2}},
       {{x2 - l2 * ct2 + w2 * st2, y2 - l2 * st2 - w2 * ct2}}}};
  std::array<double, 2> axis11{{ct1, st1}};
  std::array<double, 2> axis12{{-1 * st1, ct1}};
  std::array<double, 2> axis21{{ct2, st2}};
  std::array<double, 2> axis22{{-1 * st2, ct2}};

  auto isOverlap = [&vertex1, &vertex2](std::array<double, 2> axis) -> bool {
    double min1 = HUGE_VAL, max1 = -HUGE_VAL, min2 = HUGE_VAL, max2 = -HUGE_VAL;
    for (int i = 0; i < 4; i++) {
      double p1 = vertex1[i][0] * axis[0] + vertex1[i][1] * axis[1];
      min1 = (min1 > p1) ? p1 : min1;
      max1 = (max1 < p1) ? p1 : max1;
      double p2 = vertex2[i][0] * axis[0] + vertex2[i][1] * axis[1];
      min2 = (min2 > p2) ? p2 : min2;
      max2 = (max2 < p2) ? p2 : max2;
    }
    if (max2 < min1 || min2 > max1)
      return false;
    return true;
  };
  if (!isOverlap(axis11))
    return false;
  if (!isOverlap(axis12))
    return false;
  if (!isOverlap(axis21))
    return false;
  if (!isOverlap(axis22))
    return false;
  // If flow reached here the two rectangles are overlapping

  return true;
}

/**
 * @brief Scenario::getConflicts
 * @return all pairs of conflicts at current time
 */
std::vector<std::pair<std::string, std::string>> Scenario::getConflicts() {
  if (mCurrentSnapshotIterator == mSnapshots.end())
    return std::vector<std::pair<std::string, std::string>>();
  double time = (*mCurrentSnapshotIterator).first;
  if (mConflictMap.count(time) > 0) {
    return mConflictMap[time];
  }
  return std::vector<std::pair<std::string, std::string>>();
}
