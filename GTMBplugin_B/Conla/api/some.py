import mod.server.extraServerApi as serverApi


Id = serverApi.GetLevelId()

compCmd = serverApi.GetEngineCompFactory().CreateCommand(Id)
ServerSystem = serverApi.GetServerSystemCls()
def toscore(object, name, value):
    compCmd.SetCommand('/scoreboard players set %s %s %s' % (name, object, value))
    
def addtag(entityId, tag):
    compCmd.SetCommand('/tag %s add %s' % (serverApi.GetEngineCompFactory().CreateName(entityId).GetName(), tag))

def removetag(entityId, tag):
    compCmd.SetCommand('/tag %s remove %s' % (serverApi.GetEngineCompFactory().CreateName(entityId).GetName(), tag))