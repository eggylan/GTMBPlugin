# -*- coding: utf-8 -*-
import mod.server.extraServerApi as serverApi
CF = serverApi.GetEngineCompFactory()


# 一个玩家类 
class ServerPlayer:
    def __init__(self, playerId):
        self.playerId = playerId
        self.compPlayer = CF.CreatePlayer(playerId)
        self.compName = CF.CreateName(playerId)
        self.compDimension = CF.CreateDimension(playerId)

    def getPlayerName(self):
        return self.compName.GetName()
    
    def setPos(self, dimId, x, y, z):
        return self.compDimension.ChangePlayerDimension(dimId,x,y,z)
    
    
        