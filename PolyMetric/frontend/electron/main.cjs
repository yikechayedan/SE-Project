const { app, BrowserWindow } = require('electron')
const path = require('path')

// 屏蔽安全警告
process.env['ELECTRON_DISABLE_SECURITY_WARNINGS'] = 'true';

function createWindow () {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false // 允许跨域（可选，视情况而定）
    }
  })

  // 隐藏菜单栏 (可选)
  // win.setMenuBarVisibility(false)

  // 开发环境：加载 localhost
  // 生产环境：加载打包后的 index.html
  // 注意：这里假设开发环境你会同时运行 vite
  if (process.env.NODE_ENV === 'development' || process.argv.includes('--dev')) {
    win.loadURL('http://localhost:5173') 
    win.webContents.openDevTools() 
  } else {
    // 生产环境加载文件
    win.loadFile(path.join(__dirname, '../dist/index.html'))
  }
}

app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})