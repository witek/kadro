const {app, BrowserWindow, shell} = require('electron')
const path = require('path')
// const url = require('url')
const fs = require('fs')
const child_process = require('child_process')

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let win

const appConfigPath = app.getPath('userData')

function openBrowser(url) {
    console.log('opening: ' + url)
    shell.openExternal(url)
}

function updateFile(filepath, content, executable) {
    if (fs.existsSync(filepath)) {
        currentContent = fs.readFileSync(filepath)
    } else {
        currentContent = null;
    }
    if (currentContent == content) return

    console.log('updating: ' + filepath)

    parentDir = path.normalize(filepath + '/../')
    if (!fs.existsSync(parentDir)) {
        fs.mkdirSync(parentDir)
    }

    fs.writeFileSync(filepath, content)
    if (executable) {
        child_process.spawnSync('chmod', ['a+x', filepath]);
    }
}

function updateConfigFile(config) {
    filepath = appConfigPath + '/sites/' + config.name + '.json'
    updateFile(filepath, JSON.stringify(config), false)
}

function createWindow(config) {
    win = new BrowserWindow({title: config.title + " - Kadro",
                             width: config.width,
                             height: config.height,
                             webPreferences: {partition: "persist:" + config.name,
                                              sandbox: true,
                                              //nodeIntegration: false,
                                              //contextIsolation: true,
                                              allowpopups: false}})

    win.on('page-title-updated', (event, title) => {
        event.preventDefault()
    })

    win.on('resize', (event) => {
        size = win.getSize()
        config.width = size[0]
        config.height = size[1]
        updateConfigFile(config)
    })

    win.on('closed', () => {
        win = null
    })

    win.loadURL(config.url);

    win.webContents.on('new-window', (event, url) => {
        openBrowser(url)
        //event.preventDefault()
    })
}


function writeStartScript(configName) {
    filepath = app.getPath('home') + "/bin/" + configName
    script = "#!/bin/bash -e\n"
        + "kadro " + configName
    updateFile(filepath, script, true)
}

function writeDesktopFile(config) {
    filepath = app.getPath('home') + '/.local/share/applications/' + configName + '.desktop'
    content = '[Desktop Entry]\n'
        + 'Name=' + config.title + '\n'
        + 'Comment=Open site with Kadro: ' + config.name + ' -> ' + config.url + '\n'
        + 'Icon=' + config.name + '\n'
        + 'Exec=' + app.getPath('home') + '/bin/' + config.name + '\n'
        + 'Categories=Network;\n'
        + 'Type=Application'
    updateFile(filepath, content, false)
}

function writeConfigFile(configName, filepath) {
    config = {name: configName,
              title: configName,
              url: 'https://' + configName + '.com'}
    updateFile(filepath, JSON.stringify(config), false)
}

function start() {
    argv = process.argv
    configName = argv[argv.length-1]
    if (argv.length < 2 || configName == null) {
        console.log('Missing command line parameter: site-name')
        app.quit()
        return;
    }

    console.log("configName: " + configName)

    configFilePath = appConfigPath + '/sites/' + configName + '.json'
    console.log("configFilePath: " + configFilePath)

    if (!fs.existsSync(configFilePath)) {
        writeConfigFile(configName, configFilePath)
    }

    configData = fs.readFileSync(configFilePath)
    config = JSON.parse(configData)
    console.log("url: " + config.url)

    writeDesktopFile(config)
    writeStartScript(configName)

    console.log('')
    createWindow(config)
}

app.on('ready', start)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

let firstWindow = true

app.on('browser-window-created', (event, window) => {
    if (firstWindow) {
        firstWindow = false
        return
    }
    window.hide()
})

app.on('activate', () => {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (win === null) {
    createWindow()
  }
})

