import mod.server.extraServerApi as serverApi
serverSystem = serverApi.GetSystem('Minecraft', 'preset')
nodes = {
    'add': 'add(object, object) -> object\n将两个输入的值相加。\n\n2个输入\n1个输出',
    'print': 'print(object) -> None\n打印输入的数据。\n\n1个输入'
}
listeners = {
    'tick' : '@Listen tick()\n服务端脚本逻辑每帧执行, 每秒30帧。\n\n没有输出'
}
listenFuncName = {
    'tick': 'OnScriptTickServer'
}