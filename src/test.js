// const mongoUtils = require('./database.js');

// mongoUtils.findOne('searchres', {author:'极目新闻'}, (err, result) => {
//     if(err) 
//         console.log(err)
//     console.log(result)
// })

const MongoClient = require('mongodb').MongoClient;
const url = 'mongodb://172.17.33.149:32017'; // 替换为你的MongoDB连接字符串
const client = new MongoClient(url, { useNewUrlParser: true });

client.connect(function(err) {
  if (err) throw err;
  console.log('Connected to MongoDB');
    // 执行其他操作
});
const db = client.db('cusosint'); // 替换为你的数据库名称
const collection = db.collection('catchres'); // 替换为你的集合名称

// collection.find({}).toArray(function(err, result) {
//   if (err) throw err;
//   console.log(result);
//   client.close();
// });

try {
    collection.insertOne({name:'tom', age:20}, (err, result) => {
        if(err) {
            console.log(err)
            return
        }
        console.log(result)
    })
} catch (error) {
    
} finally {
//    client.close()
}