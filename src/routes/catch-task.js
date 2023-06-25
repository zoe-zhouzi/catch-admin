const express = require("express")
const { addOneTask, getAllCatchTask, addBatchTasks, getOneTaskResult } = require('../controllers/task-controller')

// 创建路由对象
const router = express.Router();

// 挂载路由
// 添加单条任务路由挂载
router.post('/api/addcatchtask', addOneTask)
// 查看所有的爬取任务
router.get('/api/allcatchtask', getAllCatchTask)
// 批量任务挂载路由
router.post('/api/addmultask', addBatchTasks)
// 查看结果
router.post('/api/onetaskresult', getOneTaskResult)



// 向外共享路由对象
module.exports = router