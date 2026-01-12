/* FILE_NAME: utils.js
 * AUTHRO: Zhang Zhijun
 * TIME: 2022/8/20 11:18
 * LICENSE:
*/

function parseResponseData(res) {
    console.log("response data:" + JSON.stringify(res));
    return {
        "code": res.code,
        "message": res.message,
        "data": res.data
    };
};