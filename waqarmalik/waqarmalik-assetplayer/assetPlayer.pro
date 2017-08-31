QT  += core gui opengl
CONFIG-=app_bundle

QMAKE_CFLAGS += -mmacosx-version-min=10.8
QMAKE_CXXFLAGS += -std=c++11 -stdlib=libc++ -mmacosx-version-min=10.8
QMAKE_MACOSX_DEPLOYMENT_TARGET = 10.8
LIBS += -stdlib=libc++ -mmacosx-version-min=10.8

HEADERS += src/GLWindow.H \
           src/States.H \
           src/AssetPlayer.H

SOURCES += \
        src/Main.C \
        src/GLWindow.C \
        src/States.C \
        src/AssetPlayer.C

INSTALLS += target

mac{
    dataFiles.files = data
    dataFiles.path = Contents/MacOS
    QMAKE_BUNDLE_DATA += dataFiles
}

#QMAKE_POST_LINK += $$quote(cp -R data ../assetPlayer-build/)
