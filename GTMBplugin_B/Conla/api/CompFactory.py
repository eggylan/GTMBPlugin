# uncompyle6 version 3.9.2
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:19:08) [MSC v.1500 32 bit (Intel)]
# Embedded file name: VTScripts/utils/CompFactory.py
import mod.server.extraServerApi as sapi, mod.client.extraClientApi as capi
scf = sapi.GetEngineCompFactory()

class ServerCompFactory_:

    def __init__(self):
        Id = sapi.GetLevelId()
        self.__data = {Id: {'Achievement': (scf.CreateAchievement(Id)), 
                'Action': (scf.CreateAction(Id)), 
                'ActorCollidable': (scf.CreateActorCollidable(Id)), 
                'ActorLoot': (scf.CreateActorLoot(Id)), 
                'ActorMotion': (scf.CreateActorMotion(Id)), 
                'ActorOwner': (scf.CreateActorOwner(Id)), 
                'ActorPushable': (scf.CreateActorPushable(Id)), 
                'Attr': (scf.CreateAttr(Id)), 
                'AuxValue': (scf.CreateAuxValue(Id)), 
                'Biome': (scf.CreateBiome(Id)), 
                'Block': (scf.CreateBlock(Id)), 
                'BlockEntity': (scf.CreateBlockEntity(Id)), 
                'BlockEntityData': (scf.CreateBlockEntityData(Id)), 
                'BlockInfo': (scf.CreateBlockInfo(Id)), 
                'BlockState': (scf.CreateBlockState(Id)), 
                'BlockUseEventWhiteList': (scf.CreateBlockUseEventWhiteList(Id)), 
                'Breath': (scf.CreateBreath(Id)), 
                'BulletAttributes': (scf.CreateBulletAttributes(Id)), 
                'ChatExtension': (scf.CreateChatExtension(Id)), 
                'ChestBlock': (scf.CreateChestBlock(Id)), 
                'ChunkSource': (scf.CreateChunkSource(Id)), 
                'CollisionBox': (scf.CreateCollisionBox(Id)), 
                'Command': (scf.CreateCommand(Id)), 
                'ControlAi': (scf.CreateControlAi(Id)), 
                'Dimension': (scf.CreateDimension(Id)), 
                'Effect': (scf.CreateEffect(Id)), 
                'EngineType': (scf.CreateEngineType(Id)), 
                'EntityComponent': (scf.CreateEntityComponent(Id)), 
                'EntityDefinitions': (scf.CreateEntityDefinitions(Id)), 
                'EntityEvent': (scf.CreateEntityEvent(Id)), 
                'Exp': (scf.CreateExp(Id)), 
                'Explosion': (scf.CreateExplosion(Id)), 
                'ExtraData': (scf.CreateExtraData(Id)), 
                'Feature': (scf.CreateFeature(Id)), 
                'Fly': (scf.CreateFly(Id)), 
                'Game': (scf.CreateGame(Id)), 
                'Gravity': (scf.CreateGravity(Id)), 
                'Http': (scf.CreateHttp(Id)), 
                'Hurt': (scf.CreateHurt(Id)), 
                'Interact': (scf.CreateInteract(Id)), 
                'Item': (scf.CreateItem(Id)), 
                'ItemBanned': (scf.CreateItemBanned(Id)), 
                'Loot': (scf.CreateLoot(Id)), 
                'Lv': (scf.CreateLv(Id)), 
                'MobSpawn': (scf.CreateMobSpawn(Id)), 
                'ModAttr': (scf.CreateModAttr(Id)), 
                'Model': (scf.CreateModel(Id)), 
                'MoveTo': (scf.CreateMoveTo(Id)), 
                'Msg': (scf.CreateMsg(Id)), 
                'Name': (scf.CreateName(Id)), 
                'Persistence': (scf.CreatePersistence(Id)), 
                'Player': (scf.CreatePlayer(Id)), 
                'Portal': (scf.CreatePortal(Id)), 
                'Pos': (scf.CreatePos(Id)), 
                'Projectile': (scf.CreateProjectile(Id)), 
                'Recipe': (scf.CreateRecipe(Id)), 
                'RedStone': (scf.CreateRedStone(Id)), 
                'Ride': (scf.CreateRide(Id)), 
                'Rot': (scf.CreateRot(Id)), 
                'Scale': (scf.CreateScale(Id)), 
                'Shareables': (scf.CreateShareables(Id)), 
                'Tag': (scf.CreateTag(Id)), 
                'Tame': (scf.CreateTame(Id)), 
                'Time': (scf.CreateTime(Id)), 
                'Weather': (scf.CreateWeather(Id))}}

    def remove(self, Id):
        if self.hasid(Id):
            del self.__data[Id]

    def hasid(self, Id):
        return Id in self.__data

    def hascomp(self, Id, comp):
        return comp in self.__data.get(Id, {})

    def __getattr__(self, comp):

        def inner(Id):
            if not self.hasid(Id):
                self.__data[Id] = {}
            if not self.hascomp(Id, comp):
                self.__data[Id][comp] = getattr(scf, 'Create' + comp)(Id)
            return self.__data[Id][comp]

        return inner


ServerCompFactory = ServerCompFactory_()
ccf = capi.GetEngineCompFactory()

class ClientCompFactory_:

    def __init__(self):
        Id = capi.GetLevelId()
        self.__data = {Id: {'Achievement': (ccf.CreateAchievement(Id)), 
                'Action': (ccf.CreateAction(Id)), 
                'ActorMotion': (ccf.CreateActorMotion(Id)), 
                'ActorRender': (ccf.CreateActorRender(Id)), 
                'Attr': (ccf.CreateAttr(Id)), 
                'AuxValue': (ccf.CreateAuxValue(Id)), 
                'Biome': (ccf.CreateBiome(Id)), 
                'Block': (ccf.CreateBlock(Id)), 
                'BlockGeometry': (ccf.CreateBlockGeometry(Id)), 
                'BlockInfo': (ccf.CreateBlockInfo(Id)), 
                'BlockUseEventWhiteList': (ccf.CreateBlockUseEventWhiteList(Id)), 
                'Brightness': (ccf.CreateBrightness(Id)), 
                'Camera': (ccf.CreateCamera(Id)), 
                'ChunkSource': (ccf.CreateChunkSource(Id)), 
                'CollisionBox': (ccf.CreateCollisionBox(Id)), 
                'ConfigClient': (ccf.CreateConfigClient(Id)), 
                'CustomAudio': (ccf.CreateCustomAudio(Id)), 
                'Device': (ccf.CreateDevice(Id)), 
                'Effect': (ccf.CreateEffect(Id)), 
                'EngineEffectBindControl': (ccf.CreateEngineEffectBindControl(Id)), 
                'EngineType': (ccf.CreateEngineType(Id)), 
                'Fog': (ccf.CreateFog(Id)), 
                'FrameAniControl': (ccf.CreateFrameAniControl(Id)), 
                'FrameAniEntityBind': (ccf.CreateFrameAniEntityBind(Id)), 
                'FrameAniSkeletonBind': (ccf.CreateFrameAniSkeletonBind(Id)), 
                'FrameAniTrans': (ccf.CreateFrameAniTrans(Id)), 
                'Game': (ccf.CreateGame(Id)), 
                'Health': (ccf.CreateHealth(Id)), 
                'Item': (ccf.CreateItem(Id)), 
                'ModAttr': (ccf.CreateModAttr(Id)), 
                'Model': (ccf.CreateModel(Id)), 
                'Name': (ccf.CreateName(Id)), 
                'NeteaseShop': (ccf.CreateNeteaseShop(Id)), 
                'Operation': (ccf.CreateOperation(Id)), 
                'ParticleControl': (ccf.CreateParticleControl(Id)), 
                'ParticleEntityBind': (ccf.CreateParticleEntityBind(Id)), 
                'ParticleSkeletonBind': (ccf.CreateParticleSkeletonBind(Id)), 
                'ParticleSystem': (ccf.CreateParticleSystem(Id)), 
                'ParticleTrans': (ccf.CreateParticleTrans(Id)), 
                'Player': (ccf.CreatePlayer(Id)), 
                'PlayerAnim': (ccf.CreatePlayerAnim(Id)), 
                'PlayerView': (ccf.CreatePlayerView(Id)), 
                'Pos': (ccf.CreatePos(Id)), 
                'PostProcess': (ccf.CreatePostProcess(Id)), 
                'QueryVariable': (ccf.CreateQueryVariable(Id)), 
                'Recipe': (ccf.CreateRecipe(Id)), 
                'Ride': (ccf.CreateRide(Id)), 
                'Rot': (ccf.CreateRot(Id)), 
                'SkyRender': (ccf.CreateSkyRender(Id)), 
                'Tame': (ccf.CreateTame(Id)), 
                'TextBoard': (ccf.CreateTextBoard(Id)), 
                'TextNotifyClient': (ccf.CreateTextNotifyClient(Id)), 
                'Time': (ccf.CreateTime(Id)), 
                'VirtualWorld': (ccf.CreateVirtualWorld(Id))}}

    def remove(self, Id):
        if self.hasid(Id):
            del self.__data[Id]

    def hasid(self, Id):
        return Id in self.__data

    def hascomp(self, Id, comp):
        return comp in self.__data.get(Id, {})

    def __getattr__(self, comp):

        def inner(Id):
            if not self.hasid(Id):
                self.__data[Id] = {}
            if not self.hascomp(Id, comp):
                self.__data[Id][comp] = getattr(ccf, 'Create' + comp)(Id)
            return self.__data[Id][comp]

        return inner


ClientCompFactory = ClientCompFactory_()
