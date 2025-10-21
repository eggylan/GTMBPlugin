nodes = {
    'add': 'add(object, object) -> object\n将两个输入的值相加。\n\n2个输入\n1个输出',
    'print': 'print(object) -> None\n打印输入的数据。\n\n1个输入'
}
listeners = {
    'tick' : '@Listen tick()\n服务端脚本逻辑每帧执行, 每秒30帧。\n\n没有输出',
    'addPlayer': '@Listen addPlayer(id:str, name:str, cancel:bool, msg:str)\n触发时机：准备显示“xxx加入游戏”的玩家登录提示文字时触发。\n\n4个输出'
}