import mod.server.extraServerApi as sapi
from math import floor
from CompFactory import ServerCompFactory as cr
levelId = sapi.GetLevelId()
compcmd = sapi.GetEngineCompFactory().CreateCommand(levelId)
setCommand = compcmd.SetCommand
toScore = lambda objective, value, Id, add=False: setCommand('/scoreboard players %s @s "%s" %s' % (('set', 'add')[add], objective, int(floor(value))), Id)

def toScoreEntity(objective, value, Id, add=False):
    comp = cr.Name(Id)
    name = comp.GetName()
    if name is None:
        name = ''
    comp.SetName(Id)
    setCommand('/scoreboard players %s @e[name="%s"] "%s" %s' % (('set', 'add')[add], Id, objective, int(floor(value))))
    comp.SetName(name)
    return


toScoreVirtual = lambda objective, value, name, add=False: setCommand('/scoreboard players %s "%s" "%s" %s' % (('set', 'add')[add], name, objective, int(floor(value))))
hasTag = lambda tag, Id: cr.Tag(Id).EntityHasTag(tag)
getTagList = lambda Id: cr.Tag(Id).GetEntityTags()
addTag = lambda tag, Id: cr.Tag(Id).AddEntityTag(tag)
removeTag = lambda tag, Id: cr.Tag(Id).RemoveEntityTag(tag)
modifyTag = lambda tag, condition, Id: (removeTag, addTag)[condition](tag, Id)

def removeTagStartsWith(starts, Id, except_tag=''):
    return all(map((lambda tag: removeTag(tag, Id) if tag.startswith(starts) and tag != except_tag else True), getTagList(Id)))


def hasTagStartsWith(starts, Id):
    for tag in getTagList(Id):
        if tag.startswith(starts):
            return True

    return False


def getScore(objective, Id):
    for playerScoreDict in cr.Game(levelId).GetAllPlayerScoreboardObjects():
        if playerScoreDict['playerId'] == Id:
            for scoreDict in playerScoreDict['scoreList']:
                if scoreDict['name'] == objective:
                    return scoreDict['value']

    return 0


showMsg = lambda msg, Id=None: cr.Msg(Id).NotifyOneMessage(Id, str(msg)) if Id else cr.Game(levelId).SetNotifyMsg(str(msg))

def showLineMsg(msg, Id=None, line_num=1):
    lines = ['\xc2\xa7r' if line == '' else line for line in msg.split('\n')]
    map((lambda text: showMsg(text, Id)), [('\n\xc2\xa7r').join(lines[i:i + line_num]) for i in range(0, len(lines), line_num)])


setExData = lambda key, value, Id=levelId: cr.ExtraData(Id).SetExtraData(key, value)
getExData = lambda key, Id=levelId: cr.ExtraData(Id).GetExtraData(key)
initExData = lambda key, value, Id=levelId: setExData(key, value, Id) if getExData(key, Id) is None else None
cleanExData = lambda key, Id=levelId: cr.ExtraData(Id).CleanExtraData(key)
getWholeExData = lambda Id=levelId: cr.ExtraData(Id).GetWholeExtraData()
getEntityType = lambda Id: cr.EngineType(Id).GetEngineTypeStr()

def setPlayerItem(slot_type, slot, itemDict, Id):
    compitem = cr.Item(Id)
    if slot_type == -1:
        return compitem.SpawnItemToEnderChest(itemDict, slot)
    else:
        if slot_type == 0:
            return compitem.SpawnItemToPlayerInv(itemDict, Id, slot)
        if slot_type == 2:
            return compitem.SpawnItemToPlayerCarried(itemDict, Id)
        return compitem.SetEntityItem(slot_type, itemDict, slot)
