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

#ifndef GLWINDOW_H
#define GLWINDOW_H

#include <QtGui/QWindow>
#include <QtGui/QOpenGLFunctions>

QT_BEGIN_NAMESPACE
class QPainter;
class QOpenGLContext;
class QOpenGLPaintDevice;
QT_END_NAMESPACE

class GLWindow : public QWindow, protected QOpenGLFunctions {
  Q_OBJECT
public:
  explicit GLWindow(QWindow *parent = 0);
  ~GLWindow();

  virtual void initialize();
  virtual void render(QPainter *painter);
  virtual void render();

public slots:
  void renderLater();
  void renderNow();

protected:
  bool event(QEvent *event);
  void exposeEvent(QExposeEvent *event);
  void resizeEvent(QResizeEvent *event);

private:
  bool mUpdatePending;

  QOpenGLContext *mContext;
  QOpenGLPaintDevice *mDevice;
};
#endif // GLWINDOW_H
