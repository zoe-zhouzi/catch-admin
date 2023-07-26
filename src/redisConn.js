// var redisDb = {};
// // var log4js = require('log4js');
// // log4js.configure('../config/log4j.json');
// // var logger = log4js.getLogger('redis');
// var redis = require("redis");
// var client = redis.createClient('30467', '172.17.33.149');

// client.on('error',function (err) {
//     // logger.error('redis error：'+err);
//     console.log('redis error：'+err)
// });

// client.on('connect',function () {
//     // logger.info('redis连接成功...')
//     console.log('redis连接成功')
// })

// /**
//  *
//  * @param dbNum 库号
//  * @param key 键
//  * @param value 值
//  * @param expire 过期时间（单位：秒，可为空，为空则不过期）
//  * @param callback 回调
//  */
// redisDb.set = function (dbNum,queue,key,value,expire,callback) {
//     client.select(dbNum,function (err) {
//         if (err){
//             // logger.error('redis set 选库失败：'+err);
//             console.log('redis set 选库失败：'+err);
//         }else {
//             client.hmset(queue, key,value,function (err,result) {
//                 if (err){
//                     // logger.error('redis插入失败：'+err);
//                     console.log('redis插入失败：'+err);
//                     callback(err,null);
//                     return
//                 }
//                 if (!isNaN(expire) && expire>0){
//                     client.expire(key, parseInt(expire));
//                 }
//                 callback(null,result);
//             })
//         }

//     })
// };

// redisDb.hget = function (dbNum, queue, key,callback) {
//     client.select(dbNum,function (err) {
//         if (err){
//             // logger.error('redis get 选库失败：'+err);
//             console.log('redis get 选库失败：'+err);
//         }else {
//             client.get(key,function (err,result) {
//                 if (err){
//                     // logger.error('redis获取失败：'+err);
//                     console.log('redis获取失败：'+err);
//                     callback(err,null);
//                     return
//                 }
//                 callback(null,result);
//             })
//         }
//     })
// };

// module.exports = redisDb;

// redisDb.set(
//     '15', 
//     'Cookie', "weibo", "SUB=_2A25JouVMDeRhGeNH41cT8yzKzz6IHXVq1lGErDV8PUNbmtAGLRH6kW9NSm0StgnWNKAxqw8zNZgg-4yWRi6gILZU;", 
//     3000,
//     (a, b, c) => {console.log('###a-', a, '###b-', b, '###c-', c)}
// )
// // 为啥会插入失败


const redis = require("redis");
const client = redis.createClient({url: 'redis://172.17.33.149:30467/15'})
client.hset('cookies', 'wb', '123456')

// const set = async () => {
//     //  client.hSet('cookies', 'wb', '123456')
//      await client.hset('key', 'field', 'value');
// }
// set()