const path = require('path')
// const connection = require('../database.js')
const mongoUtils = require('../database.js');
const pythonProcess = require('../utils/call-py.js'); // 引入调用py文件的模块

const callSpider = async (url) => {
    return new Promise((resolve) => {
        console.log('-----进来了callSpider-----')
        let fileName = ''
        let type = ''
        console.log('-----url-----', url)
        try {
            if(url.indexOf('toutiao')!=-1) {
                fileName = '02_toutiao_right.py';
                type = '头条'
            } else if(url.indexOf('baidu')!=-1 || url.indexOf('baijiahao')!=-1) {
                fileName = '04_baijiahao_right.py';
                type = '百家号'
            } else if(url.indexOf('www.163.com') != -1) {
                fileName = '03_wangyi_right.py';
                type = '网易'
            } else if(url.indexOf('sohu')!=-1) {
                fileName = '05_souhu.py';
                type = '搜狐'
            } else if(url.indexOf('weibo.com')!=-1) {
                fileName = '07_weibo.py';
                type = '微博'
            } else if(url.indexOf('kuaishou')!=-1) {
                fileName = '08_kuaishou.py';
                type = '快手'
            } else if(url.indexOf('weixin.qq')!=-1) {
                fileName = '09_weixin.py';
                type = '微信'
            } else if(url.indexOf('bilibili')!=-1) {
                fileName = '06_bilibili.py';
                type = '哔哩哔哩'
            } else {
                console.log('###else处的不正常0')
                resolve(0)
            }
        } catch (error) {
            console.log('###', error)
        }
        console.log('来了吗')
        mongoUtils.findOne('searchres', {url: url}, async (result) => {
            if(result == 0) {
                console.log('mongodb查询findOne查询出错')
                resolve(0)
            }
            console.log('-----数据查询的搜索结果-----', typeof result);
            // 如果数据库返回的结果为空，就进行搜索
            if(!result) {
                let filepath = path.join(appRoot, 'pyspider', fileName)
                console.log('----调用python爬虫程序前---');
                await pythonProcess.executePythonScript(filepath, url).then((result) => {
                    console.log('----调用python爬虫程序后的回调---','爬取数据成功', '返回1');
                    resolve(1)
                }, (err) => {
                    console.log('----调用python爬虫程序后的回调---','爬取数据失败', err, '返回0');
                    resolve(0)
                });
            } else {
                console.log('----不需要调用爬虫，数据库有数据，返回1----')
                resolve(1)
            }
        })
    })
}

const addOneTask = async (req, res) => {
    console.log('有人访问了服务器', req.body)
    // 1 要添加爬取任务到数据库，这个需要有返回，判断是否添加成功
    let id = req.body.id
    let url = req.body.taskinput
    let task = {
        _id: id,
        taskname: req.body.taskname,
        tasktype: req.body.tasktype,
        taskinput: url,
        createtime: req.body.createtime,
        istrackauthor: req.body.istrackauthor,
        taskstatus: req.body.taskstatus
    }
    mongoUtils.insertOne('catchtask', task, async (err, result) => {
        if(err) {
            return err
        } else {
            res.send(result)
        }
    })
    // 2 调用爬虫程序，这个不返回
    // 如果数据库有存在结果，就不调用爬虫程序，不需要呈现数据出来
    // const isSuccess = 
    console.log('status有值前')
    const status = (await callSpider(url)) ? '执行成功' : '执行失败'
    console.log('status有值')
    console.log('###isSuccess', status)
    // 3 根据2才能有任务表中执行状态的变更
    console.log(`-----进行状态的变更，修改${id}的状态-----`)
    const a = mongoUtils.updateOne('catchtask', {_id: id}, {$set: {taskstatus: status}}, (result) => {
        if(result == 0) {
            console.log(`-----进行状态的变更，${id}执行失败-----`)
            return '状态变更失败'
        } 
        console.log(`-----进行状态的变更，${id}执行成功-----`)
        return result
    })
}

const getAllCatchTask = async (req, res) => {
    mongoUtils.findAll('catchtask', {}, (result) => {
        if(result == 0) {
            console.log('-----查询结果执行成功-----')
            return '查询所有的爬取任务失败'
        }
        console.log('----查询所有的爬取任务成功-----')
        console.log(result)
        res.send(result)
    })
}

const addBatchTasks = async (req, res) => {
    console.log('有人访问了服务器', req.body)
    // 1 要添加爬取任务到数据库，这个需要有返回，判断是否添加成功
    let id = req.body.id
    let urlArray = req.body.urlArray
    // let urlArrStr = JSON.stringify(urlArray)
    let task = {
        _id: id,
        taskname: req.body.taskname,
        tasktype: req.body.tasktype,
        taskinput: req.body.taskinput,
        createtime: req.body.createtime,
        istrackauthor: req.body.istrackauthor,
        taskstatus: req.body.taskstatus
    }
    mongoUtils.insertOne('catchtask', task, (result) => {
        if(result == 0) {
            return 
        } else {
            // res.send(result)
            res.end('批量爬虫任务添加成功')
        }
    })
    // 2 批量执行任务
    for(let i=0; i<urlArray.length; i++) {
        // 1 想让每条任务都作为一条任务添加到数据库
        // 2 执行每条任务的爬虫
        const isSuccess = await callSpider(urlArray[i])
        const status = isSuccess ? '执行成功' : '执行失败'
        let task = {
            _id: id+i,
            taskname: req.body.taskname,
            tasktype: req.body.tasktype,
            taskinput: urlArray[i],
            createtime: req.body.createtime,
            istrackauthor: req.body.istrackauthor,
            taskstatus: status
        }
        const a = mongoUtils.insertOne('catchtask', task, (result) => {
            if(result == 0) {
                return '插入失败'
            } else {
                // res.send(result)
            }
        })
        console.log(a)
    }
    
}

const getOneTaskResult = async (req, res) => {
    console.log('有人访问了服务器', req.body.url)
    mongoUtils.findOne('searchres', {url: req.body.url}, (result) => {
        if(result == 0) {
            console.log('-----查询结果执行成功-----')
            return '查询所有的爬取任务失败'
        } 
        console.log('----查询所有的爬取任务成功-----')
        console.log(result)
        res.send(result)
    })
} 
module.exports.addOneTask = addOneTask
module.exports.getAllCatchTask = getAllCatchTask
module.exports.addBatchTasks = addBatchTasks
module.exports.getOneTaskResult = getOneTaskResult