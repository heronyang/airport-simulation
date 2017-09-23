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

#include <QtGui>
#include <QOpenGLBuffer>
#include <QOpenGLTexture>
#include <QString>
#include <QtCore/qmath.h>
#include <QDateTime>
#include <iostream>
#include <fstream>
#include <sstream>
#include <cassert>
#include <vector>
#include "AssetPlayer.H"

AssetPlayer::AssetPlayer(std::string airport, std::string trackFile, bool doConflict, bool colorScheme)
    : mAirport(airport),
      mTrackFile(trackFile),
      mSurfaceQuadsPosition(QOpenGLBuffer::VertexBuffer),
      mSurfaceQuadsColor(QOpenGLBuffer::VertexBuffer),
      mColorScheme(colorScheme) {
  this->setTitle("ASSET Player");
  this->resize(1280, 800);
  this->setMinimumWidth(800);
  this->setMinimumHeight(600);
  this->mIsPlayer = (trackFile == "") ? false : true;

  if (mIsPlayer) {
    this->mDoConflict = doConflict;
    this->mData = std::shared_ptr<Scenario>(new Scenario(trackFile, mDoConflict));
    this->mCurrentTime = mData->setIterator(0, mSnapshot);
  }

  this->mTopButtonStatus.fill(false);
  this->mTopButtonText = {{QStaticText("Reset View"), QStaticText("SDSS Nodes"), QStaticText("Node Names"),
                           QStaticText("SDSS Links"), QStaticText("Aircraft IDs")}};
  for (auto &ii : mTopButtonText)
    ii.setPerformanceHint(QStaticText::AggressiveCaching);

  this->mBottomButtonStatus.fill(false);
  this->mBottomButtonText = {{QStaticText("    -"), QStaticText("    +"), QStaticText("  Play"),
                              QStaticText(" Pause"), QStaticText("   < >")}};
  for (auto &ii : mBottomButtonText)
    ii.setPerformanceHint(QStaticText::AggressiveCaching);

  this->mSlideLen = width() - mSlideX0 - mBottomButtonWidth;

  mWorldTransform.reset();
  mWorldTransform = mWorldTransform.translate(width() / 2, height() / 2);
  mMousePosition = QPointF(width() / 2, height() / 2);
  mPanTranslate = QPointF(0, 0);
  mTimerId = startTimer(50);
}

AssetPlayer::~AssetPlayer() {
  mSurfaceQuadsPosition.destroy();
  mSurfaceQuadsColor.destroy();
}

void AssetPlayer::timerEvent(QTimerEvent *event) {
  if (event->timerId() == mTimerId) {
    mCount += 0.05;
    if (mIsPlayer && mPlay) {
      double step = ((mRewind) ? -1.0 : 1.0) * 0.05 * mSpeed;
      this->mCurrentTime = mData->getSnapshot(step, mSnapshot);
      mSlidePercent = this->mCurrentTime / mData->getSimLength();

      // Reset acTrack is aircraft is no longer in simulation
      if (mAircraftTrack != "") {
        if (mSnapshot.count(mAircraftTrack) == 0)
          mAircraftTrack = "";
      }
    }
    renderLater();
  }
}

void AssetPlayer::wheelEvent(QWheelEvent *event) {
  if (event->pos().y() > 20 && event->pos().y() < height() - 20) {
    QPointF numPixels = event->pixelDelta();
    QPointF numDegrees = event->angleDelta();

    if (!numPixels.isNull()) {
      mScale += numPixels.y() / 100.0;
    } else if (!numDegrees.isNull()) {
      mScale += numDegrees.y() / 120.0;
    }
    double scale_max = 10;
    double scale_min = 0.1;
    mScale = (mScale > scale_max) ? scale_max : ((mScale < scale_min) ? scale_min : mScale);
    mMousePosition = event->pos();
    renderNow();
  }
  event->accept();
}

void AssetPlayer::mousePressEvent(QMouseEvent *event) {
  if (event->pos().y() > 20 && event->pos().y() < height() - 20) {
    mMousePressPosition = event->pos();
  } else if (event->pos().y() < 20 && event->pos().x() < int(mTopButtonStatus.size()) * 100) {
    int index = int(event->pos().x() / 100);
    mTopButtonStatus[index] = true;
    switch (index) {
      case 0:
        break;
      case 1:
        mShowNodes = !mShowNodes;
        break;
      case 2:
        mShowNodeNames = !mShowNodeNames;
        break;
      case 3:
        mShowLinks = !mShowLinks;
        break;
      case 4:
        mShowACID = !mShowACID;
        break;
      default:
        std::cout << "(WWW) Can't determine what button was pressed." << std::endl;
        break;
    }
  } else if (event->pos().y() > height() - 20) {
    int x = event->pos().x();
    unsigned long ii;
    for (ii = 0; ii < mBottomButtonX.size(); ++ii) {
      if (x > mBottomButtonX[ii] && x < mBottomButtonX[ii] + mBottomButtonWidth) {
        mBottomButtonStatus[ii] = true;
        break;
      }
    }
    switch (ii) {
      //        case 0:
      //            speed = (speed>1 && speed<=30) ? speed-1 : speed;
      //            break;
      //        case 1:
      //            speed = (speed>=1 && speed<30) ? speed+1 : speed;
      //            break;
      case 2:
        mPlay = true;
        break;
      case 3:
        mPlay = false;
        break;
      case 4:
        mRewind = !mRewind;
        break;
      case 5:
        if (x > mSlideX0 && x < mSlideX0 + mSlideLen)
          mSliderMove = true;
        break;
      default:
        break;
    }
  }
  event->accept();
}

void AssetPlayer::mouseMoveEvent(QMouseEvent *event) {
  bool doMove = true;
  for (auto &bt : mTopButtonStatus)
    doMove = doMove && !bt;
  for (auto &bt : mBottomButtonStatus)
    doMove = doMove && !bt;
  doMove = doMove && !mSliderMove;
  if (doMove && event->pos().y() > 20 && event->pos().y() < height() - 20) {
    if (event->buttons() & Qt::LeftButton) {
      mPanTranslate =
          mWorldTransform.inverted().map(event->pos()) - mWorldTransform.inverted().map(mMousePressPosition);
      renderNow();
      mMousePressPosition = event->pos();
      this->mPanMode = true;
    } else
      mMousePosition = event->pos();
  } else if (mSliderMove && event->pos().y() > height() - 20 && event->pos().x() > mSlideX0 &&
             event->pos().x() < mSlideX0 + mSlideLen) {
    mSlidePercent = double(event->pos().x() - mSlideX0) / mSlideLen;
    this->mCurrentTime = mData->setIterator(mSlidePercent * 100, mSnapshot);
  }
  event->accept();
}

void AssetPlayer::mouseReleaseEvent(QMouseEvent *event) {
  if (event->pos().y() < 20) {
    if (mTopButtonStatus[0] == true) {
      mScale = 1;
      mWorldTransform.reset();
      mWorldTransform = mWorldTransform.translate(width() / 2, height() / 2);
      mMousePosition = QPointF(width() / 2, height() / 2);
      mPanTranslate = QPointF(0, 0);
    }
  } else if (event->pos().y() > height() - 20) {
    if (mSliderMove && event->pos().x() > mSlideX0 && event->pos().x() < mSlideX0 + mSlideLen) {
      mSlidePercent = double(event->pos().x() - mSlideX0) / mSlideLen;
      this->mCurrentTime = mData->setIterator(mSlidePercent * 100, mSnapshot);
    }
    mSliderMove = false;
  } else if (mIsPlayer) { // within map: check click on ac_icon
    if (this->mPanMode)
      this->mPanMode = false;
    else {
      mAircraftTrack = "";
      QPointF click = mWorldTransform.inverted().map(event->pos());
      double dist = 100;
      for (auto ac : mSnapshot) {
        double sqDist = (ac.second.x - click.x()) * (ac.second.x - click.x()) +
                        (ac.second.y + click.y()) * (ac.second.y + click.y());
        if (sqDist < 100 && sqDist < dist) {
          mAircraftTrack = ac.first;
          dist = sqDist;
          mGetTrack = true;
        }
      }
    }
  }
  for (auto &bt : mTopButtonStatus)
    bt = false;
  for (auto &bt : mBottomButtonStatus)
    bt = false;
  mSliderMove = false;

  event->accept();
}

void AssetPlayer::keyPressEvent(QKeyEvent *event) {
  switch (event->key()) {
    case Qt::Key_Space:
      this->mShowBbox = true;
      break;
    default:
      QWindow::keyPressEvent(event); // Let base class handle the other keys
  }
}

void AssetPlayer::keyReleaseEvent(QKeyEvent *event) {
  switch (event->key()) {
    case Qt::Key_Space:
      this->mShowBbox = false;
      break;
    default:
      QWindow::keyPressEvent(event); // Let base class handle the other keys
  }
}

void AssetPlayer::setPanZoom(QPainter *p) {
  p->setRenderHint(QPainter::Antialiasing);
  QPointF mouseWorldPositionOld = mWorldTransform.inverted().map(mMousePosition);
  QPointF oldOrigin = mWorldTransform.map(QPointF(0, 0));

  p->translate(oldOrigin.x(), oldOrigin.y());
  p->scale(mScale, mScale);
  mWorldTransform = p->worldTransform();
  QPointF mouseWorldPositionNew = mWorldTransform.inverted().map(mMousePosition);
  p->translate(mouseWorldPositionNew.x() - mouseWorldPositionOld.x(),
               mouseWorldPositionNew.y() - mouseWorldPositionOld.y());

  p->translate(mPanTranslate);
  mPanTranslate = QPointF(0, 0);

  mWorldTransform = p->worldTransform();
}

void AssetPlayer::nativePainting() {
  // Draw Background
  mSurfaceQuadsPosition.bind();
  glEnableClientState(GL_VERTEX_ARRAY);
  glVertexPointer(3, GL_FLOAT, 0, 0);
  mSurfaceQuadsColor.bind();
  glEnableClientState(GL_COLOR_ARRAY);
  glColorPointer(3, GL_FLOAT, 0, 0);
  glDrawArrays(GL_QUADS, 0, mVertexCount);
  glDisableClientState(GL_VERTEX_ARRAY);
  glDisableClientState(GL_COLOR_ARRAY);
  mSurfaceQuadsPosition.release();
  mSurfaceQuadsColor.release();
  // Draw SDSS Nodes
  if (mShowNodes) {
    mNodePosition.bind();
    glEnableClientState(GL_VERTEX_ARRAY);
    glVertexPointer(3, GL_FLOAT, 0, 0);
    mNodeColor.bind();
    glEnableClientState(GL_COLOR_ARRAY);
    glColorPointer(3, GL_FLOAT, 0, 0);
    glDrawArrays(GL_QUADS, 0, mNodeCount);
    glDisableClientState(GL_VERTEX_ARRAY);
    glDisableClientState(GL_COLOR_ARRAY);
    mNodePosition.release();
    mNodeColor.release();
  }
  // Draw SDSS Link
  if (mShowLinks) {
    mLinkPosition.bind();
    glEnableClientState(GL_VERTEX_ARRAY);
    glVertexPointer(3, GL_FLOAT, 0, 0);
    mLinkColor.bind();
    glEnableClientState(GL_COLOR_ARRAY);
    glColorPointer(3, GL_FLOAT, 0, 0);
    glDrawArrays(GL_LINES, 0, mLinkCount);
    glDisableClientState(GL_VERTEX_ARRAY);
    glDisableClientState(GL_COLOR_ARRAY);
    mLinkPosition.release();
    mLinkColor.release();
  }
  if (mIsPlayer) {
    drawAircraftTrack();
    // drawAircrafts();
    drawAircraftsTextured();
  }
}

void AssetPlayer::drawAircrafts() {
  for (auto ac : mSnapshot) {
    if (mData->getAircraftStatus(ac.first)) {
      glColor3f(0.0f, 0.0f, 0.0f);
      drawAircraftOutline(ac.second.x, ac.second.y, -ac.second.head, 1.0);
      glColor3f(0.0f, 1.0f, 0.4f);
      drawAircraft(ac.second.x, ac.second.y, -ac.second.head, 1.0);
    } else {
      glColor3f(0.0f, 0.0f, 0.0f);
      drawAircraftOutline(ac.second.x, ac.second.y, -ac.second.head, 1.0);
      glColor3f(0.0f, 0.7f, 1.0f);
      drawAircraft(ac.second.x, ac.second.y, -ac.second.head, 1.0);
    }
  }
}

void AssetPlayer::drawAircraftsTextured() {
  const GLshort Texcoords[] = {0, 0, 1, 0, 1, 1, 0, 1};
  const GLfloat ACVert[] = {-0.5f, -0.5f, 0.5f, -0.5f, 0.5f, 0.5f, -0.5f, 0.5f};

  glEnable(GL_TEXTURE_2D);
  glEnable(GL_BLEND);
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
  glDisableClientState(GL_COLOR_ARRAY);
  glEnableClientState(GL_VERTEX_ARRAY);
  glEnableClientState(GL_TEXTURE_COORD_ARRAY);
  glVertexPointer(2, GL_FLOAT, 0, ACVert);
  glTexCoordPointer(2, GL_SHORT, 0, Texcoords);
  if (mDoConflict)
    drawConflicts();
  for (auto &ac : mSnapshot) {
    std::string model = mData->getAircraftType(ac.first);
    if (mAircraftTexture.count(model) == 0) {
      std::cout << ac.first << " is " << model << " that is not present in database" << std::endl;
      model = "default";
    }
    if (mShowBbox) {
      if (ac.second.conflict)
        drawBbox(ac.second.x, ac.second.y, ac.second.head, ac.second.speed, mAircraftTextureSize[model].first,
                 mAircraftTextureSize[model].second, 1.0, 0.0, 0.0, 0.2);
      else
        drawBbox(ac.second.x, ac.second.y, ac.second.head, ac.second.speed, mAircraftTextureSize[model].first,
                 mAircraftTextureSize[model].second, 0.0, 0.0, 0.0, 0.2);
    }
    glPushMatrix();
    if (mData->getAircraftStatus(ac.first)) { // Departure
      if (ac.second.status == "GATE/DEP")
        glColor4f(0.0f, 1.0f, 0.4f, 0.5f);
      else if (ac.second.speed < 1)
        glColor4f(0.0f, 0.5f, 0.2f, 1.0f);
      else
        glColor4f(0.0f, 1.0f, 0.4f, 1.0f);
    } else {
      if (ac.second.status == "GATE")
        glColor4f(0.0f, 0.7f, 1.0f, 0.5f);
      else if (ac.second.speed < 1)
        glColor4f(0.0f, 0.35f, 0.5f, 1.0f);
      else
        glColor3f(0.0f, 0.7f, 1.0f);
    }
    mAircraftTexture[model]->bind();
    glTranslatef(ac.second.x, ac.second.y, 0);
    glRotatef(-ac.second.head, 0, 0, 1);
    glScalef(mAircraftTextureSize[model].first, mAircraftTextureSize[model].first, 0);
    glDrawArrays(GL_QUADS, 0, 4);
    glPopMatrix();
    mAircraftTexture[model]->release();
  }
  glDisableClientState(GL_TEXTURE_COORD_ARRAY);
  glDisableClientState(GL_VERTEX_ARRAY);
  glDisable(GL_BLEND);
  glDisable(GL_TEXTURE_2D);
}

void AssetPlayer::drawBbox(double x, double y, double th, double v, double l, double w, float r, float g,
                           float b, float a) {
  glPushMatrix();
  glColor4f(r, g, b, a);
  glTranslatef(x, y, 0);
  glRotatef(-th, 0, 0, 1);

  // Draw bounding box dependent on speed. Change also in Scenario.isConflict
  double yTrans = std::min(0.3, v / 30); // 6m/s = 0.2, 9m/s = 0.3
  double yScale = 0.5 / (0.5 - yTrans);

  glScalef(w, yScale * l, 0);
  glTranslatef(0.0, yTrans, 0.0);
  glDrawArrays(GL_QUADS, 0, 4);
  glPopMatrix();
}

void AssetPlayer::drawConflicts() {
  std::vector<std::pair<std::string, std::string>> conflicts = mData->getConflicts();
  if (conflicts.empty())
    return;
  for (auto &conflict : conflicts) {
    if (mSnapshot.count(conflict.first) == 0 || mSnapshot.count(conflict.second) == 0) {
      std::cout << "(WWW) __" << __FILE__ << __LINE__ << " : " << mCurrentTime << " " << conflict.first << " "
                << conflict.second << std::endl;
      continue;
    }
    State ac1 = mSnapshot.at(conflict.first);
    State ac2 = mSnapshot.at(conflict.second);
    std::string model1 = mData->getAircraftType(conflict.first);
    std::string model2 = mData->getAircraftType(conflict.second);
    if (mAircraftTextureSize.count(model1) == 0)
      model1 = "default";
    if (mAircraftTextureSize.count(model2) == 0)
      model2 = "default";
    glPushMatrix();
    float green = (ac1.conflict && ac2.conflict) ? 0.0f : 1.0f;
    glColor4f(1.0f, green, 0.0f, 0.2f);
    glLineWidth(5.0);
    glBegin(GL_LINES);
    glVertex3f(ac1.x, ac1.y, 0);
    glVertex3f(ac2.x, ac2.y, 0);
    glEnd();
    glLineWidth(2.0);
    glPopMatrix();
    drawBbox(ac1.x, ac1.y, ac1.head, ac1.speed, mAircraftTextureSize[model1].first,
             mAircraftTextureSize[model1].second, 1.0, green, 0.0, 0.2);
    drawBbox(ac2.x, ac2.y, ac2.head, ac2.speed, mAircraftTextureSize[model2].first,
             mAircraftTextureSize[model2].second, 1.0, green, 0.0, 0.2);
  }
}

void AssetPlayer::drawAircraft(double x, double y, double phi, double scale) {
  glPushMatrix();
  glTranslatef(x, y, 0);
  glRotatef(phi, 0, 0, 1);
  glScalef(scale, scale, 1.0);
  // Wings
  glBegin(GL_TRIANGLE_STRIP);
  glVertex2f(0.0f, 10.0f);
  glVertex2f(-20.0f, 4.0f);
  glVertex2f(-20.0f, 0.0f);
  glVertex2f(0.0f, 2.0f);
  glVertex2f(0.0f, 10.0f);
  glEnd();
  glBegin(GL_TRIANGLE_STRIP);
  glVertex2f(0.0f, 10.0f);
  glVertex2f(0.0f, 2.0f);
  glVertex2f(20.0f, 0.0f);
  glVertex2f(20.0f, 4.0f);
  glVertex2f(0.0f, 10.0f);
  glEnd();
  // Tail
  glBegin(GL_TRIANGLE_STRIP);
  glVertex2f(0.0f, -14.0f);
  glVertex2f(-6.0f, -16.0f);
  glVertex2f(-6.0f, -18.0f);
  glVertex2f(0.0f, -17.0f);
  glVertex2f(0.0f, -14.0f);
  glEnd();
  glBegin(GL_TRIANGLE_STRIP);
  glVertex2f(0.0f, -14.0f);
  glVertex2f(0.0f, -17.0f);
  glVertex2f(6.0f, -18.0f);
  glVertex2f(6.0f, -16.0f);
  glVertex2f(0.0f, -14.0f);
  glEnd();
  // Body
  glBegin(GL_TRIANGLE_STRIP);
  glVertex2f(0.0f, 20.0f);
  glVertex2f(-3.0f, 18.0f);
  glVertex2f(3.0f, 18.0f);
  glVertex2f(-2.0f, -20.0f);
  glVertex2f(2.0f, -20.0f);
  glEnd();
  glPopMatrix();
}

void AssetPlayer::drawAircraftOutline(double x, double y, double phi, double scale) {
  double pad = 0.5;
  glPushMatrix();
  glTranslatef(x, y, 0);
  glRotatef(phi, 0, 0, 1);
  glScalef(scale, scale, 1.0);
  // Wings
  glBegin(GL_TRIANGLE_STRIP);
  glVertex2f(0.0f, 10.0f + pad);
  glVertex2f(-20.0f - pad, 4.0f + pad);
  glVertex2f(-20.0f - pad, 0.0f - pad);
  glVertex2f(0.0f, 2.0f - pad);
  glVertex2f(0.0f, 10.0f + pad);
  glEnd();
  glBegin(GL_TRIANGLE_STRIP);
  glVertex2f(0.0f, 10.0f + pad);
  glVertex2f(0.0f - pad, 2.0f - pad);
  glVertex2f(20.0f + pad, 0.0f - pad);
  glVertex2f(20.0f + pad, 4.0f + pad);
  glVertex2f(0.0f, 10.0f + pad);
  glEnd();
  // Tail
  glBegin(GL_TRIANGLE_STRIP);
  glVertex2f(0.0f, -14.0f + pad);
  glVertex2f(-6.0f - pad, -16.0f + pad);
  glVertex2f(-6.0f - pad, -18.0f - pad);
  glVertex2f(0.0f, -17.0f - pad);
  glVertex2f(0.0f, -14.0f + pad);
  glEnd();
  glBegin(GL_TRIANGLE_STRIP);
  glVertex2f(0.0f, -14.0f + pad);
  glVertex2f(0.0f - pad, -17.0f - pad);
  glVertex2f(6.0f + pad, -18.0f - pad);
  glVertex2f(6.0f + pad, -16.0f + pad);
  glVertex2f(0.0f, -14.0f + pad);
  glEnd();
  // Body
  glBegin(GL_TRIANGLE_STRIP);
  glVertex2f(0.0f, 20.0f + pad);
  glVertex2f(-3.0f - pad, 18.0f + pad);
  glVertex2f(3.0f + pad, 18.0f + pad);
  glVertex2f(-2.0f - pad, -20.0f - pad);
  glVertex2f(2.0f + pad, -20.0f - pad);
  glEnd();
  glPopMatrix();
}

void AssetPlayer::drawAircraftTrack() {
  if (mAircraftTrack == "")
    return;
  if (mGetTrack) {
    mTrackData = mData->getAircraftTrack(mAircraftTrack);
    mGetTrack = false;
  }
  glColor3f(0.7f, 0.0f, 0.0f);
  glLineWidth(3.0f);
  glBegin(GL_LINE_STRIP);
  for (auto track : mTrackData)
    glVertex2f(track.x, track.y);
  glEnd();
}

void AssetPlayer::initialize() {
  if (mColorScheme)
    glClearColor(0.0f, 0.168627f, 0.2117647f, 1.0f);
  else
    glClearColor(0.99216f, 0.96471f, 0.890196f, 1.0f);
  glShadeModel(GL_SMOOTH);
  glEnable(GL_LINE_SMOOTH);
  glDisable(GL_DEPTH_TEST);
  glDisable(GL_LIGHTING);

  surfaceVBOs();
  sdssNodeVBOs();
  sdssLinkVBOs();

  std::ifstream inFile("data/images/aircraft_texture_size.txt");
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
      mAircraftTexture[model] =
          std::unique_ptr<QOpenGLTexture>(new QOpenGLTexture(QImage(texture_file.c_str()).mirrored()));
      mAircraftTexture[model]->setMinificationFilter(QOpenGLTexture::LinearMipMapLinear);
      mAircraftTexture[model]->setMagnificationFilter(QOpenGLTexture::Linear);
      mAircraftTextureSize[model] = std::make_pair(length, wingspan);
    }
    while (ss >> tmp) {
    };
    ss.str("");
    ss.clear();
    line = "";
  }
}

void AssetPlayer::surfaceVBOs() {
  std::string filename = "data/" + mAirport + "/";
  for (auto &ch : mAirport)
    filename += std::tolower(ch);
  filename += ".quad";
  std::ifstream surfaceQuads(filename);
  assert(surfaceQuads);
  float x, y, z, r, g, b;
  z = 0;
  std::vector<float> vertices;
  std::vector<float> colors;
  std::string line, tmp;
  std::stringstream ss;
  while (getline(surfaceQuads, line)) {
    if (line.size() > 0 && line[line.size() - 1] == '\r')
      line.resize(line.size() - 1);
    while (!line.empty() && *line.begin() == ' ')
      line.erase(line.begin());
    if (!line.empty() && line.size() > 0 && line[0] != '#') {
      ss << line;
      ss >> x >> y >> r >> g >> b;
      vertices.push_back(x);
      vertices.push_back(y);
      vertices.push_back(z);
      colors.push_back(r);
      colors.push_back(g);
      colors.push_back(b);
    }
    while (ss >> tmp) {
    };
    ss.str("");
    ss.clear();
    line = "";
  }
  mVertexCount = vertices.size();
  mSurfaceQuadsPosition.create();
  mSurfaceQuadsPosition.setUsagePattern(QOpenGLBuffer::StaticDraw);
  mSurfaceQuadsPosition.bind();
  mSurfaceQuadsPosition.allocate(&vertices[0], mVertexCount * sizeof(float));

  mSurfaceQuadsColor.create();
  mSurfaceQuadsColor.setUsagePattern(QOpenGLBuffer::StaticDraw);
  mSurfaceQuadsColor.bind();
  mSurfaceQuadsColor.allocate(&colors[0], mVertexCount * sizeof(float));

  mSurfaceQuadsPosition.release();
  mSurfaceQuadsColor.release();
}

void AssetPlayer::sdssNodeVBOs() {
  std::string filename = "data/" + mAirport + "/nodes.quad";
  std::ifstream nodeQuads(filename);
  assert(nodeQuads);
  float x, y, z, r, g, b;
  z = 0;
  std::vector<float> vertices;
  std::vector<float> colors;
  std::string line, tmp;
  std::stringstream ss;
  int index = 0;
  while (getline(nodeQuads, line)) {
    if (line.size() > 0 && line[line.size() - 1] == '\r')
      line.resize(line.size() - 1);
    while (!line.empty() && *line.begin() == ' ')
      line.erase(line.begin());
    if (!line.empty() && line.size() > 0 && line[0] != '#') {
      ss << line;
      ss >> tmp >> x >> y >> r >> g >> b;
      if (index % 4 == 0) {
        tmp += " (" + std::to_string(index / 4) + ")";
        mNodeNames.push_back(std::make_tuple(QStaticText(tmp.c_str()), x, y));
      }
      ++index;
      vertices.push_back(x);
      vertices.push_back(y);
      vertices.push_back(z);
      colors.push_back(r);
      colors.push_back(g);
      colors.push_back(b);
    }
    while (ss >> tmp) {
    };
    ss.str("");
    ss.clear();
    line = "";
  }
  for (auto &ii : mNodeNames)
    std::get<0>(ii).setPerformanceHint(QStaticText::AggressiveCaching);

  mNodeCount = vertices.size();
  mNodePosition.create();
  mNodePosition.setUsagePattern(QOpenGLBuffer::StaticDraw);
  mNodePosition.bind();
  mNodePosition.allocate(&vertices[0], mNodeCount * sizeof(float));

  mNodeColor.create();
  mNodeColor.setUsagePattern(QOpenGLBuffer::StaticDraw);
  mNodeColor.bind();
  mNodeColor.allocate(&colors[0], mNodeCount * sizeof(float));

  mNodePosition.release();
  mNodeColor.release();
}

void AssetPlayer::sdssLinkVBOs() {
  std::string filename = "data/" + mAirport + "/links.quad";
  std::ifstream linkQuads(filename);
  assert(linkQuads);
  float x, y, z, r, g, b;
  z = 0;
  std::vector<float> vertices;
  std::vector<float> colors;
  std::string line, tmp;
  std::stringstream ss;
  while (getline(linkQuads, line)) {
    if (line.size() > 0 && line[line.size() - 1] == '\r')
      line.resize(line.size() - 1);
    while (!line.empty() && *line.begin() == ' ')
      line.erase(line.begin());
    if (!line.empty() && line.size() > 0 && line[0] != '#') {
      ss << line;
      ss >> x >> y >> r >> g >> b;
      vertices.push_back(x);
      vertices.push_back(y);
      vertices.push_back(z);
      colors.push_back(r);
      colors.push_back(g);
      colors.push_back(b);
    }
    while (ss >> tmp) {
    };
    ss.str("");
    ss.clear();
    line = "";
  }
  mLinkCount = vertices.size();
  mLinkPosition.create();
  mLinkPosition.setUsagePattern(QOpenGLBuffer::StaticDraw);
  mLinkPosition.bind();
  mLinkPosition.allocate(&vertices[0], mLinkCount * sizeof(float));

  mLinkColor.create();
  mLinkColor.setUsagePattern(QOpenGLBuffer::StaticDraw);
  mLinkColor.bind();
  mLinkColor.allocate(&colors[0], mLinkCount * sizeof(float));

  mLinkPosition.release();
  mLinkColor.release();
}

void AssetPlayer::render(QPainter *p) {
  mSlideLen = width() - mSlideX0 - mBottomButtonWidth;

  setPanZoom(p);
  p->save();
  p->scale(1, -1);
  p->beginNativePainting();
  nativePainting();
  p->endNativePainting();
  p->restore();

  // Draw SDSS Node Name
  if (mShowNodes && mShowNodeNames && mScale > 2) {
    p->save();
    p->setPen(QColor(211, 54, 130, 225));
    p->scale(1, -1);
    QTransform screen = p->transform();
    p->setWorldMatrixEnabled(false);
    for (auto ii : mNodeNames) {
      QPointF textloc = screen.map(QPointF(std::get<1>(ii), std::get<2>(ii)));
      p->drawStaticText(textloc, std::get<0>(ii));
    }
    p->restore();
  }

  // Aircraft label
  if (mIsPlayer && mShowACID && mScale > 0.5) {
    p->save();
    p->setPen(QColor(203, 75, 22));
    p->scale(1, -1);
    QTransform screen = p->transform();
    p->setWorldMatrixEnabled(false);
    for (auto ac : mSnapshot) {
      QRectF rect(screen.map(QPointF(ac.second.x, ac.second.y)), QSizeF(100, 50));
      QString txt;
      if (mScale > 1)
        txt = QString::fromStdString(ac.first + "\n" + mData->getAircraftType(ac.first));
      else
        txt = QString::fromStdString(ac.first);
      p->drawText(rect, Qt::AlignLeft | Qt::AlignTop, txt);
    }
    p->restore();
  }

  drawMenuBars(p);
  drawHud(p);
}

void AssetPlayer::drawMenuBars(QPainter *p) {
  p->save();
  p->setWorldMatrixEnabled(false);

  QRect topRect(0, 0, width(), 20);
  QRect bottomRect(0, height() - 20, width(), 20);
  QLinearGradient topGradient(topRect.topLeft(), topRect.bottomLeft());
  topGradient.setColorAt(1, QColor(160, 160, 160));
  topGradient.setColorAt(0, QColor(220, 220, 220));
  QLinearGradient bottomGradient(bottomRect.topLeft(), bottomRect.bottomLeft());
  bottomGradient.setColorAt(0, QColor(160, 160, 160));
  bottomGradient.setColorAt(1, QColor(220, 220, 220));

  // Top and Bottom bars
  p->fillRect(topRect, topGradient);
  p->fillRect(bottomRect, bottomGradient);

  // Top Buttons
  unsigned long numTop = (mIsPlayer) ? mTopButtonStatus.size() : mTopButtonStatus.size() - 1;
  for (unsigned long i = 0; i < numTop; ++i) {
    if (mTopButtonStatus[i]) {
      p->setBrush(bottomGradient);
      p->setPen(QColor(255, 255, 255));
    } else {
      p->setBrush(topGradient);
      p->setPen(QColor(100, 100, 100));
    }
    p->drawRect(QRectF(i * 100, 0, 100, 19));
    p->setPen(QColor(0, 0, 0));
    p->drawStaticText(QPoint(100 * i + 10, 2), QStaticText(mTopButtonText[i]));
  }

  // Bottom Status
  if (mIsPlayer) {
    for (unsigned long i = 0; i < mBottomButtonStatus.size(); ++i) {
      if (mBottomButtonStatus[i]) {
        p->setBrush(topGradient);
        p->setPen(QColor(255, 255, 255));
      } else {
        p->setBrush(bottomGradient);
        p->setPen(QColor(100, 100, 100));
      }
      p->drawRect(QRectF(mBottomButtonX[i], height() - 19, mBottomButtonWidth, 19));
      p->setPen(QColor(0, 0, 0));
      p->drawStaticText(QPoint(mBottomButtonX[i] + 2, height() - 18), QStaticText(mBottomButtonText[i]));
    }

    p->setBrush(QColor(225, 225, 225));
    p->drawRect(QRectF(mBottomButtonWidth, height() - 19, mBottomButtonX[1] - mBottomButtonWidth, 19));
    p->drawText(mBottomButtonWidth + 7, height() - 5, QString("%1").arg(mSpeed, 2));

    p->setPen(QColor(50, 50, 50));
    p->setBrush(topGradient);
    p->drawRect(QRectF(mSlideX0, height() - 11, mSlideLen, 2));
    p->drawText(width() - mBottomButtonWidth + 10, height() - 5,
                QString::number(int(mSlidePercent * 100)) + "%");
    p->setPen(QColor(100, 100, 100));
    p->setBrush(bottomGradient);
    p->drawRect(QRectF(mSlideX0 + mSlidePercent * mSlideLen, height() - 17, 7, 14));
  }

  if (mBottomButtonStatus[0]) {
    mSpeed = (mSpeed > 1 && mSpeed <= 30) ? mSpeed - 1 : mSpeed;
  } else if (mBottomButtonStatus[1]) {
    mSpeed = (mSpeed >= 1 && mSpeed < 30) ? mSpeed + 1 : mSpeed;
  }
  p->setPen(Qt::NoPen);
  p->restore();
}

void AssetPlayer::drawHud(QPainter *p) {
  p->save();
  p->setWorldMatrixEnabled(false);

  // HUD
  if (mIsPlayer) {
    QDateTime dt;
    dt.setTime_t(mData->getUtcStartTime());
    QString str = "Simulation time: " + QString::number(mData->getSimStartTime() + this->mCurrentTime) +
                  "\r\nCount: " + QString::number(mCount) + "\r\nSize: A" + QString::number(mSnapshot.size()) +
                  "  C" + QString::number(mData->getConflicts().size()) + "\r\n" + dt.toString();
    QRect hudRect(5, 25, 220, 75);
    int pad = 5;
    p->setPen(QColor(0, 0, 0));
    p->setBrush(QColor(0, 0, 0, 100));
    p->drawRect(hudRect);
    p->setPen(QColor(250, 250, 250));
    p->drawText(hudRect.adjusted(pad, pad, -pad, -pad), str);
  }

  p->setPen(QColor(100, 0, 100));
  QTransform windowToWorld = p->worldTransform().inverted();
  QPointF mouseWorldPosition = windowToWorld.map(mMousePosition);
  p->drawText(10, height() - 70, QString("x = %1, y = %2").arg(QString::number(mouseWorldPosition.x()),
                                                               QString::number(-mouseWorldPosition.y())));
  p->drawText(10, height() - 50, QString("Scale: %3").arg(QString::number(mScale)));
  p->setBrush(Qt::NoBrush);
  p->setPen(Qt::NoPen);
  p->restore();
}
