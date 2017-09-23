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

#ifndef ASSETPLAYER_H
#define ASSETPLAYER_H

#include <array>
#include <vector>
#include <tuple>
#include <memory>
#include "GLWindow.H"
#include "States.H"

/**
 * @brief The AssetPlayer class
 * Extends the GLWindow class and adds the actual display for a given airport.
 * The member variable mData stores the complete scenario/track_information.
 */
class AssetPlayer : public GLWindow {
public:
  AssetPlayer(std::string mAirport, std::string mTrackFile, bool doConflict, bool mColorScheme);
  ~AssetPlayer();

protected:
  void initialize();
  void render(QPainter *painter);
  void timerEvent(QTimerEvent *event);
  void wheelEvent(QWheelEvent *event);
  void mousePressEvent(QMouseEvent *event);
  void mouseReleaseEvent(QMouseEvent *event);
  void mouseMoveEvent(QMouseEvent *event);
  void keyPressEvent(QKeyEvent *event);
  void keyReleaseEvent(QKeyEvent *event);
  void setPanZoom(QPainter *p);
  void drawMenuBars(QPainter *p);
  void drawHud(QPainter *p);
  void nativePainting();
  void drawAircraftsTextured();
  void drawConflicts();
  void drawBbox(double x, double y, double th, double v, double l, double w, float r, float g, float b,
                float a);
  void drawAircrafts();
  void drawAircraft(double x, double y, double phi, double mScale);
  void drawAircraftOutline(double x, double y, double phi, double mScale);
  void drawAircraftTrack();
  void surfaceVBOs();
  void sdssNodeVBOs();
  void sdssLinkVBOs();

private:
  double mCount = 0;      // Actual elapsed time
  std::string mAirport;   // The airport
  std::string mTrackFile; // the *.asset track file
  bool mColorScheme;      // ColorScheme
  bool mDoConflict;       // Should we do conflict check
  bool mIsPlayer;         // True if we have a good track file that will be played

  std::shared_ptr<Scenario> mData;                  // The complete track information
  std::unordered_map<std::string, State> mSnapshot; // current snapshot
  double mCurrentTime = 0;                          // the current simulation time
  std::string mAircraftTrack = "";                  // Aircraft for which track will be displayed
  std::vector<State> mTrackData;                    // The tracks for the chosen aircraft
  bool mGetTrack = false;                           // Used to extract the track only once.

  double mScale = 0.5;
  int mTimerId;
  QTransform mWorldTransform;
  QPointF mMousePosition;
  QPointF mMousePressPosition;
  QPointF mPanTranslate;
  bool mPanMode = false;

  // Top bar, buttons, and associated values
  std::array<bool, 5> mTopButtonStatus;
  std::array<QStaticText, 5> mTopButtonText;
  bool mShowNodes = false;
  bool mShowNodeNames = false;
  bool mShowLinks = false;
  bool mShowACID = false;
  bool mShowBbox = false;

  // bottom bar, buttons and associated values
  std::array<bool, 5> mBottomButtonStatus;
  std::array<QStaticText, 5> mBottomButtonText;
  std::array<int, 5> mBottomButtonX = {{0, 80, 250, 300, 350}};
  int mBottomButtonWidth = 50;
  int mSpeed = 1;
  bool mPlay = false;
  bool mRewind = false;

  // Slider on bottom bar used to seek playback.
  bool mSliderMove = false;
  double mSlidePercent = 0;
  int mSlideX0 = 420;
  int mSlideLen;

  // Opengl textures for aircraft, buffers for surface data.
  std::unordered_map<std::string, std::unique_ptr<QOpenGLTexture>> mAircraftTexture;
  std::unordered_map<std::string, std::pair<double, double>> mAircraftTextureSize;
  QOpenGLBuffer mSurfaceQuadsPosition;
  QOpenGLBuffer mSurfaceQuadsColor;
  int mVertexCount;
  std::vector<std::tuple<QStaticText, float, float>> mNodeNames;
  QOpenGLBuffer mNodePosition;
  QOpenGLBuffer mNodeColor;
  int mNodeCount;
  QOpenGLBuffer mLinkPosition;
  QOpenGLBuffer mLinkColor;
  int mLinkCount;
};

#endif // ASSETPLAYER_H
