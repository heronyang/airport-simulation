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

#include <QtCore/QCoreApplication>
#include <QtGui/QOpenGLContext>
#include <QtGui/QOpenGLPaintDevice>
#include <QtGui/QPainter>

#include "GLWindow.H"

GLWindow::GLWindow(QWindow *parent) : QWindow(parent), mUpdatePending(false), mContext(0), mDevice(0) {
  setSurfaceType(QWindow::OpenGLSurface);
}

GLWindow::~GLWindow() { delete mDevice; }

void GLWindow::initialize() {}

bool GLWindow::event(QEvent *event) {
  switch (event->type()) {
    case QEvent::UpdateRequest:
      renderNow();
      return true;
    default:
      return QWindow::event(event);
  }
}

void GLWindow::exposeEvent(QExposeEvent *event) {
  Q_UNUSED(event);

  if (isExposed())
    renderNow();
}

void GLWindow::resizeEvent(QResizeEvent *event) {
  Q_UNUSED(event);

  if (isExposed())
    renderNow();
}

void GLWindow::renderNow() {
  if (!isExposed())
    return;

  mUpdatePending = false;
  bool needsInitialize = false;
  if (!mContext) {
    mContext = new QOpenGLContext(this);
    mContext->setFormat(requestedFormat());
    mContext->create();
    needsInitialize = true;
  }
  mContext->makeCurrent(this);
  if (needsInitialize) {
    initializeOpenGLFunctions();
    initialize();
  }
  render();
  mContext->swapBuffers(this);
}

void GLWindow::render() {
  if (!mDevice)
    mDevice = new QOpenGLPaintDevice;
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);
  // mDevice->setSize(size());
  mDevice->setSize(size() * devicePixelRatio());
  mDevice->setDevicePixelRatio(devicePixelRatio());
  QPainter painter(mDevice);
  render(&painter);
}

void GLWindow::render(QPainter *painter) {
  QRectF rect;
  int pad = 10;
  painter->setBrush(QColor(0, 0, 0, 10));
  painter->drawText(QRectF(0, 0, width(), height()), Qt::AlignCenter, QStringLiteral("Waqar Malik"), &rect);
  painter->drawRect(rect.adjusted(-pad, -pad, pad, pad));
}

void GLWindow::renderLater() {
  if (!mUpdatePending) {
    mUpdatePending = true;
    QCoreApplication::postEvent(this, new QEvent(QEvent::UpdateRequest));
  }
}
