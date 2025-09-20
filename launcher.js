

var content="yJinW1VDTfWuUtA_GsfzQf06RtLhQAaxb3QEbmkSkAA"
// 导入的库写最上面

// (1) 导入代理器
const { get_environment } = require('./proxy.js');
// (2) 定义要代理的对象（你原来的 proxy_array）
const proxy_array = ['window', 'document', 'location', 'navigator', 'history', 'screen', 'Object', 'localStorage'];

// (3) 放补的环境 👈 你在这里根据报告手动补！
// 示例（根据你实际需要调整）：

// 重写console.log。，自己定义开关
let log_flag = true;
function vlog(){
    if(log_flag){
        console.log(...arguments);
        }
};

// 重写空方法
_null = function(){
    console.log("方法:", "console.log  ", "对象:", "console",
            "  参数:", arguments);
	// 不用返回数据，只是一个空方法
	// return null;
}

window = global;
document = {}
// location = {}
window.top = window;
window.addEventListener = _null;

setInterval = _null;
clearInterval = _null;
setTimeout = _null;
clearTimeout = _null;
location = {
    "ancestorOrigins": {},
    "href": "https://www.ouyeel.com/steel/search?pageIndex=0&pageSize=50",
    "origin": "https://www.ouyeel.com",
    "protocol": "https:",
    "host": "www.ouyeel.com",
    "hostname": "www.ouyeel.com",
    "port": "",
    "pathname": "/steel/search",
    "search": "",
    "hash": ""
};
div = {
    getElementsByTagName:function(arg){
        vlog("方法:", "getElementsByTagName  ", "对象:", "document",
            "  参数:", arg);
        if(arg==='i'){
            return {length:0};
        }
    }
}
meta = {
    length:2,
    content:content,
    getAttribute:function(arg){
        vlog("方法:", "getAttribute  ", "对象:", "meta",
            "  参数:", arg);
        if(arg==='r'){
            return "m";
        }
    },
    parentNode:{
        removeChild:_null
    }
}
document = {
    createElement: function(arg){
        vlog("方法:", "createElement  ", "对象:", "document",
            "  参数:", arg);
        if(arg==='div'){
            return div;
        }
    },
    appendChild:_null,
    getElementById:_null,
    removeChild:_null,
    // addEventListener:_null,
    // attachEvent:_null,
    getElementsByTagName:function(arg){
        vlog("方法:", "getElementsByTagName  ", "对象:", "document",
            "  参数:", arg);
        if(arg==='script'){
            return {
                "0": {},
                "1": {}
            };
        }
        if(arg==='meta'){
            return [meta,meta];
        }
        if(arg==='base'){
            return {};
        }
    },
}

// (4) 启动代理
get_environment(proxy_array);

// (5) 运行你的目标脚本
require('./1/RsTs.js');
require('./1/RsExecEnv.js');

// 测试访问
console.log("\n🧪 测试访问:");
console.log("document.cookie:", document.cookie);
// console.log("navigator.userAgent:", navigator.userAgent);