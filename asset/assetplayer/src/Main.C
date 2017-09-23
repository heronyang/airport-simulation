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
#include <iostream>
#include <string>
#include "AssetPlayer.H"

//#include "states.H"

int main(int argc, char **argv) {
  std::string airport = "";
  std::string trackFile = "";
  bool doConflict = false;
  bool dark = false;
  for (int i = 1; i < argc; ++i) {
    std::string cmdLine = argv[i];
    size_t pos = cmdLine.find("help");
    if (pos != std::string::npos) {
      std::cout << "\n\tUsage: ./assetPlayer --airport=<ICAO> --track=<filename>" << std::endl;
      std::cout << "\t\t airport: (required) Use ICAO code" << std::endl;
      std::cout << "\t\t track: (optional) specify the filename of history "
                << "file in ASSET format\n" << std::endl;
      return 0;
    }
    pos = cmdLine.find("airport");
    if (pos != std::string::npos) {
      airport = cmdLine.substr(pos + 8);
      continue;
    }
    pos = cmdLine.find("track");
    if (pos != std::string::npos) {
      trackFile = cmdLine.substr(pos + 6);
      continue;
    }
    pos = cmdLine.find("conflict");
    if (pos != std::string::npos) {
      doConflict = true;
      continue;
    }
    pos = cmdLine.find("dark");
    if (pos != std::string::npos) {
      dark = true;
      continue;
    }
    std::cout << "(EEE) Unknown parameter provided." << std::endl;
  }
  for (auto &ch : airport)
    ch = std::toupper(ch);
  if (airport == "") {
    std::cout << "(EEE) Need airport information.\n"
              << "\t`./assetPlayer --help` for more options" << std::endl;
    return 0;
  }
  if (trackFile.find_last_of(".") != std::string::npos) {
    if (trackFile.substr(trackFile.find_last_of(".") + 1) != "asset") {
      std::cout << "(EEE) Need track data in ASSET format.\n"
                << "\t`./assetPlayer --help` for more options" << std::endl;
      return 0;
    }
  } else if (trackFile != "") {
    std::cout << "(EEE) Need track data in ASSET format.\n"
              << "\t`./assetPlayer --help` for more options" << std::endl;
    return 0;
  }

  QGuiApplication app(argc, argv);

  QSurfaceFormat format;
  format.setSamples(4);

  AssetPlayer display(airport, trackFile, doConflict, dark);
  display.setFormat(format);
  // display.showMaximized();
  display.show();

  app.exec();
}
