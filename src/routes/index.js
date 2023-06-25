const express = require("express")
const taskRouter = require('./catch-task')

const router = express.Router();

// 注册使用
router.use(taskRouter)

module.exports = router
