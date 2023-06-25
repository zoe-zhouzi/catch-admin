const { spawn } = require('child_process');

function executePythonScript(scriptPath, url) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', [scriptPath]);

    // 向python脚本传参
    pythonProcess.stdin.write(url)
    pythonProcess.stdin.end()

    let data = "";
    let error = "";

    pythonProcess.stdout.on("data", (chunk) => {
      data += chunk;
    });

    pythonProcess.stderr.on("data", (chunk) => {
      error += chunk;
    });

    pythonProcess.on("exit", (code) => {
      if (code === 0) {
        console.log('###', data)
        // resolve(JSON.parse(data));
        resolve(data);
      } else {
        reject(error || `Python script exited with code ${code}.`);
      }
    });
  });
}

module.exports.executePythonScript= executePythonScript;
// 调用executePythonScript函数，并处理返回值或错误信息
// executePythonScript('path/to/python/script.py')
//   .then((result) => {
//     console.log(result);
//   })
//   .catch((error) => {
//     console.error(error);
//   });
