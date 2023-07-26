const MongoClient = require('mongodb').MongoClient;
// 数据库连接 URL
const url = 'mongodb://172.17.33.149:32017';
const client = new MongoClient(url);


module.exports = {
    connect: function(callback) {
        client.connect(err => {
            if (err) throw err;
            console.log("Connected to MongoDB");
            callback();
          });
    },
    insertOne: function(collectionName, data, callback) {
        const db = client.db("cucosint");
        const collection = db.collection(collectionName);
        collection.insertOne(data).then(result => {
            callback(result)
        }).catch(error => {
            callback(0)
        })
    },
    findOne: function(collectionName, filter, callback) {
        const db = client.db("cucosint");
        const collection = db.collection(collectionName);
        try {
            collection.findOne(filter).then(result => {
                callback(result)
            }).catch(error => {
                callback(0)
            })
        } catch (error) {
            console.log(error)
        }
    },
    findAll: function(collectionName, filter, callback) {
        const db = client.db("cucosint");
        const collection = db.collection(collectionName);
        collection.find(filter).toArray().then(result => {
            callback(result)
        }).catch(error => {
            callback(0)
        })
    },
    updateOne: function(collectionName, filter, update, callback) {
        const db = client.db("cucosint")
        const collection = db.collection(collectionName);
        collection.updateOne(filter, update).then(result => {
            callback(result)
        }).catch(error => {
            callback(0)
        });
    },
    deleteOne: function(collectionName, filter, callback) {
        const db = client.db("cucosint");
        const collection = db.collection(collectionName);
        collection.deleteOne(filter).then(result => {
            callback(result)
        }).catch(error => {
            callback(0)
        });
    },
};

