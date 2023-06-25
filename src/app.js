const path = require('path')

// path.resolve 将路径或路径片段的序列解析为绝对路径。
// 这里表示的到 catch-admin 的绝对路径（包括catch-admin）
global.appRoot = path.resolve(__dirname, '..')
const express = require('express');
const app = express();
const router = require('./routes/index')

// 如果传入json类型，必须要有这个中间件，否则收不到数据
app.use(express.json())

// 注册路由模块
app.use(router)

// 设置 public 为静态文件的存放文件夹
app.use('/public', express.static('public'));

// 主页
app.get('/', function(req, res) {
    res.send('Hello World');
})

const server = app.listen(5001, function() {
    const host = server.address().address
    const port = server.address().port
    console.log(`Node.JS 服务器已启动，访问地址： http://${host}:${port}`)
})