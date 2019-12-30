![](https://github.com/mbuckaway/CallupSeedingMgr/workflows/CallupSeedingMgr_Build/badge.svg)

# Call Up Seeding Manager

Welcome to Call Up Seeding Manager. Call Up Seeding Manager is software used to score bike races. It has many features including support for RFID chip readers. Full documentation is in the CallupSeedingMgrHtml directory or under Help in the application.

## User Installation

As a user, you can install CrossManager on Windows, Mac OSX, and Linux. Only x86 64 bit platforms are supported. CallupSeedingMgr has gone through many iterations. Previous versions require Mac and Linux users to install Python, the source code, and fight with it to get it working. This is no longer the case. As with the Windows version, the MacOSX and Linux versions are available as binary releases. The MacOSX and Linux versions are built on github as a release automatically when the code changes. See the Releases tab in the github repo for binaries.

### Windows Installation

From the Releases tab, download the CallupSeedingMgr-Setup_x64_VERSION.exe file. Run the file and follow the on screen instructions. By default, the program will be installed in C:\Program Files\CallupSeedingMgr. You can find Crossmgr from the start menu in the CallupSeedingMgr program group.

When running the installer, Windows will complain that it is a unknown publish. Click the MORE INFORMATION link in that dialog, and then click the RUN ANYWAYS button. The install will proceed.

CallupSeedingMgrImpinj, TagReadWriter, CallupSeedingMgrAlien, CallupSeedingMgrVideo, and SeriesMgr follow the same install process. They will all install into the CallupSeedingMgr program group.

### Mac OSX Installation

From the Releases tab, download the CallupSeedingMgr-VERSION.dmg file. From the finder, double click the DMG file to open it. Once the window comes up, you simply drag and drop the CallupSeedingMgr.app folder to your Applications directory. From the Applications folder, you can now run CallupSeedingMgr like any other Mac app. Most recent Mac OSX versions will require you to press CTRL before clicking on the app for the first time, and then clicking open. The app is a non-signed program that MacOSX will not open otherwise. This is only require the first time you run it. MacOSX will also ask a few questions when the program is run, and you must confirm with YES (Allow Networking, Access to Documents Directory, etc, etc.)

CallupSeedingMgrImpinj, TagReadWriter, CallupSeedingMgrAlien, CallupSeedingMgrVideo, and SeriesMgr follow the same install process.

#### Debugging the Mac Apps

Because MacOSX has added a lot of security to the system, some weird problems can occur that prevent the application from starting. First, and foremost, because the apps are not signed, you must CTRL-CLICK the icon, and select Open from the pop up menu, and then click Open on the dialog box to start the application the first time. Additionally, MacOSX will prompt the user for permissions to access the network, documents folder, etc.. Sometimes, the splash screens for the application will cover this dialog box up, or it could end up behind the application. Unless you select ALLOW, the application can't work. For example, CallupSeedingMgr requires network access to run. Additionally, sometimes the application just won't start. Typically, it's icon will start to flash, and then nothing. To see why and what is happening, run the application from the command line from the app's MacOS directory. For example, for CallupSeedingMgr:

```bash
cd /Applications/CallupSeedingMgr.app/Content/MacOS
./CallupSeedingMgr
```

Python is setup to dump logs to stdout which usually indicates the problem. Sometimes, the problem of starting the application will just go away.

### Linux Installation

Download the CallupSeedingMgr-VERSION.AppImage file. Store this file in a convenient location such as $HOME/bin. Make the executable with

```bash
chmod 755 CallupSeedingMgr-VERSION.AppImage
```

Next, just run the AppImage with:

```bash
./CallupSeedingMgr-VERSION.AppImage
```

...from the command prompt.

CallupSeedingMgrImpinj, TagReadWriter, CallupSeedingMgrAlien, CallupSeedingMgrVideo, and SeriesMgr follow the same install process.

Alternative, setup a desktop icon to call it directly.

## Building Call Up Seeding Manager

There are two scripts to build CallupSeedingMgr and the associated tools. One for Linux/Mac and one for Windows. Each platform has a build script to install the dependancies, build the binaries for the application, and package the programs.

| Script  | Help Parameter |Purpose |
|---------|---------|--------|
| compile.sh | -h | Linux/MacOSX Build script |
| compile.ps1 | -help | Windows build script |

Use the help parameter to find the available command line options. You can build programs individual or run parts of the build process individual using different command line options.

All platforms currently work with Python 3.7.x. Python 3.8 and newer is not yet supported by pyinstaller which freezes the python code to binary form.

Windows builds require InnoSetup V6.x from [https://www.jrsoftware.org/isdl.php]. If you do not have Inno Setup installed, the windows build will fail.

The build has been automated, and compile.sh/ps1 script does everything to enable the developer to build CallupSeedingMgr and the associated tools. However, you can also download the binary from the github Releases tab.

Linux dependancies are contained in the linuxdeps.sh script. The linuxdeploy-plugin-appimage-x86_64.AppImage binary is required from https://github.com/linuxdeploy/linuxdeploy-plugin-appimage. The compile.sh script will download linuxdeploy-plugin-appimage if it does not exist in the current directory automatically.

The build procedure for Linux and MacOSX platforms are as follows:

- Install the Linux dependancies (Linux only!)

```bash
  bash linuxdeps.h
```

- Setup a virtual env, download the required python modules:

```bash
bash compile.sh -S
```

- Build all the code and publish to releases directory

```bash
bash compile.sh -A
```

When the build is complete, the resultant DMG/AppImage files will be in the release directory. The above process is what the build.yml Workflow file (.github/workflows/build.yaml) uses to build the code on GitHub.

The build procedure for windows are as follows:

- Setup a virtual env, download the required python modules:

```powershell
.\compile.ps1 -setupenv
```

- Build all the code and publish to releases directory

```powershell
.\compile.ps1 -everything
```
When the build is complete, the resultant exe installer files will be in the release directory. The above process is what the build.yml Workflow file (.github/workflows/build.yaml) uses to build the code on GitHub.

### Making a Release

With the workflow setup on Github, builds are automatic. Every time a change it checked into the repo, github will build the code. The purpose of this build is to ensure the code will build on all platforms. To make a release, a tag is added to the repo. When a tag is added, it will appear in the releases tab, and github will run the workflow to build the code for MacOSX, Linux, and Windows.

To make a release, do the following:

Linux/Mac:

```bash
bash compile.sh -T
```

Windows:

```powershell
.\compile.ps1 -tag
```

This will tag the repo and cause github to build the code and create a new release.
