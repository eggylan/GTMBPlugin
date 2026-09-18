# `get_status`

完整状态名、点路径和示例见 [`STATUS_REFERENCE.md`](STATUS_REFERENCE.md)。

```
/get_status <目标> <状态或 Molang 表达式>
/get_status <目标> <状态或 Molang 表达式> toscore <积分榜目标> <set|add|remove> [scale]
/get_status <目标> <状态或 Molang 表达式> totag <标签名> [结果为 false / 空时删除]
/set_status <目标> <状态> <值>
/set_status <目标> <状态> normal <值>
/set_status <目标> <状态> toscore <计分项> [计分实体]
```

`scale` 默认是 `1`。积分榜写入会计算 `round(结果 * scale)`，因此可用 `10`、`100` 保存浮点精度。

## 示例

```mcfunction
/get_status @s xyz
/get_status @s position.x
/get_status @s rotxy
/get_status @s rotation.yaw
/get_status @s velocity.x
/get_status @s isFlying
/get_status @s effects
/get_status @s effect.speed.duration
/get_status @s item.carried
/get_status @s item.carried.durability
/get_status @s item.inventory.0
/get_status @s world.time
/get_status @s xp
/get_status @s max_health
/get_status @s "query.health * 100" toscore hp100 set 1
/get_status @a "query.health" toscore health add 10
/get_status @s "query.health > 0" totag alive true
/get_status @s all
/set_status @s hunger 6
/set_status @s position 100,64,-20
/set_status @s position.x 100
/set_status @s rotation.yaw 180
/set_status @s velocity 0,0.4,1
/set_status @s velocity.x 0.25
/set_status @s natural_regen 0
/set_status @s abilities.canFly 1
/set_status @s isFlying 1
/set_status @s effect.speed 30,1,1
/set_status @s effect.speed 0
/set_status @s item.carried.durability 100
/set_status @s item.inventory.0.count 32
/set_status @s attributes.health 20
/set_status @s tag.boss 1
/set_status @s extra.home "{\"x\":100,\"y\":64,\"z\":-20}"
/set_status @s hunger normal 6
/set_status @s hunger toscore hunger_score
/set_status @a hunger toscore hunger_score @s
```

### `set_status` 模式

- `normal <值>`：手动写入；例如 `/set_status @s hunger normal 6`。
- 省略模式仍兼容旧写法 `/set_status @s hunger 6`，等同于 `normal`。
- `toscore <计分项> [计分实体]`：先读取计分项的整数值，再逐个写入目标状态；未填写计分实体时读取当前目标自身，填写选择器时可用一个实体，或与目标数量相同的实体列表。

### 数学表达式

普通表达式支持 `+ - * / % **`、`& | ^ << >>`、比较、Python 风格 `and/or/not`，以及 `abs`、`sqrt`、`floor`、`ceil`、`round`、`sin`、`cos`、`tan`、`asin`、`acos`、`atan`、`atan2`、`log`、`log10`、`exp`、`pow`、`min`、`max`、`clamp`、`lerp`、`hypot` 等函数。状态路径可直接使用分量形式：

```mcfunction
/get_status @s "sqrt(velocity.x*velocity.x+velocity.z*velocity.z)"
/get_status @s "max_health-health"
/get_status @s "(hunger>=6) and (health>0)"
```

以 `query.`、`variable.` 开头的表达式，以及使用 `&&`、`||`、`!` 的 Molang 表达式交给服务端 Molang 求值器；例如 `/get_status @s query.is_flying`。

### `extern` 派生状态

本插件提供只读状态：`extern.forward`、`extern.backward`、`extern.leftward`、`extern.rightward`、`extern.rising`、`extern.falling`、`extern.downing`、`extern.climbing`。水平状态是按实体 yaw 分解后的速度分量，垂直状态是速度分量的正值，`climbing` 使用 `query.is_on_ladder`；`/get_status @s extern` 返回全部派生状态。

表达式原样交给 ModSDK 3.9 的 `EvalMolangExpression`，以目标实体作为 `query` 上下文；可直接传入 `query.*`，以及引擎支持的算术、比较、逻辑、移位、异或等 Molang 运算。

## 服务端直接状态

- 空间：`position` / `position.x|y|z`、`foot_position` / `.x|y|z`、`rotation` / `.pitch|yaw`、`velocity` / `.x|y|z`。旧名称 `xyz`、`rotxy`、`motion`、`vx` / `vy` / `vz` 仍可用。
- 实体：`id`、`name`、`type`、`alive`、`tags`、`nbt`、`extra_data`、`components`、`motions`、`properties`、`on_fire`、`step_height`
- 属性：`health`、`max_health`，以及 `speed`、`damage`、`hunger`、`saturation`、`absorption`、`armor`、`attack_speed`、`flying_speed`、`block_break_speed` 等全部 ModSDK `AttrType`；任一属性都可加 `max_` 前缀。
- 玩家：`xp`、`xp_percent`、`total_xp`、`level`、`exhaustion`、`max_exhaustion`、`health_level`、`starve_level`、`health_tick`、`starve_tick`、`natural_regen`、`natural_starve`、`can_fly`、`isFlying` / `is_flying`、`abilities`、`abilities.<字段>`、`permission`、`game_type`、`sneaking`、`swimming`、`blocking`、`fishing`、`interact_range`、`respawn_pos`。
- 其他：`air`、`max_air`、`tag.<标签名>`、`extra.<键>[.<嵌套键>]`、`nbt.<键>[.<嵌套键>]`。
- 状态效果：`effects`、`effect.<效果名>`、`effect.<效果名>.duration`、`.duration_f`、`.amplifier`、`.active`，以及 `loaded_effects`。
- 物品：`item.carried` / `item.mainhand` / `held_item`、`item.offhand`、`item.inventory`、`item.inventory.<槽位>`、`item.armor.<槽位>`。物品字典完整返回原版与 `userData`、附魔等字段；可追加 `.durability` 或 `.max_durability`。
- 实体组件：攻击目标、主人、骑乘者、实体缩放、重力、跳跃力、AI、碰撞箱、氧气消耗、实体定义状态（幼年、驯服、坐下、剪毛、掉落物、变种、交易等级等）均可用对应英文状态名直接读取，`all.entity_states` 会汇总。
- 世界：`world.time`、`world.raining`、`world.thunder`、`world.game_type`、`world.difficulty`、`world.game_rules`、`world.gravity`、`world.seed`、`world.spawn_position`、`world.spawn_dimension`、`world.scoreboard_objects`。

`all` 返回上述可安全快照的聚合结果；聊天回显截断在 1024 字符，完整数据建议拆成单项读取。

## 事件与客户端状态

- `event.<服务端事件名>[.<字段路径>]`：第一次调用按需订阅事件；事件下一次触发后，再次执行即可取得最近一次快照。例如：`event.PlayerAttackEntityEvent.playerId`。
- `client.query.*`：向对应玩家客户端点对点请求客户端 Molang query；结果异步回传后显示或执行 `toscore` / `totag`。
- 其他客户端直接状态：`client.dimension`、`client.body_rot`、`client.on_ground`、`client.in_lava`、`client.all`。
- `client.event.<客户端事件名>[.<字段路径>]`：同样按需订阅并读取最近事件快照。

事件监听上限为每端 32 个，客户端请求队列上限 128 个；没有命令调用时不会注册监听、轮询或运行 Tick。

## `set_status` 可写状态

所有布尔状态均统一接受 `true` / `false` 或 `1` / `0`；其中 `1` 为真、`0` 为假。数组可写成 `x,y,z` 或 JSON 数组 `[x,y,z]`。

- 空间：`position`、`position.x|y|z`、`rotation`、`rotation.pitch|yaw`、`velocity`、`velocity.x|y|z`。`velocity` 是 ModSDK 的瞬时运动向量；玩家使用 `SetPlayerMotion`，其他实体使用 `SetMotion`。
- 全部 `AttrType` 属性：例如 `health`、`max_health`、`speed`、`max_speed`、`damage`、`hunger`、`absorption`、`armor`、`flying_speed`、`block_break_speed` 等。
- 实体：`name`、`step_height`、`air`、`max_air`、`tag.<标签名>`、`extra.<键>[.<嵌套键>]`。
- 状态效果：`effect.<效果名>`。`0` 删除效果；单个数值表示秒数；`秒数,等级,粒子` 添加或刷新，例如 `effect.speed 30,1,1`。
- 物品：`item.carried`、`item.offhand`、`item.inventory.<槽位>`、`item.armor.<槽位>` 可用 JSON 物品字典替换；也可写 `.count`、`.userData.*`、`.durability`、`.max_durability`。
- 自定义状态：`mod.<键>` 使用 ModAttr 读取和写入任意 ModSDK 自定义属性。
- 玩家：`hunger`、`current_exhaustion`、`max_exhaustion`、`health_level`、`starve_level`、`health_tick`、`starve_tick`、`natural_regen`、`natural_starve`、`jumpable`、`movable`、`can_fly`、`isFlying` / `is_flying`、`attack_mobs`、`attack_players`、`build_ability`、`mine_ability`、`open_containers`、`operate_doors`、`operator_commands`、`teleport_ability`、`muted`、`ban_fishing`、`permission`、`game_type`、`interact_range`、`pickup_area`、`attack_speed_amplifier`。

属性也可写为 `attributes.health` / `attributes.max_health`；玩家状态可写为 `player.hunger`；能力别名支持 `abilities.canFly`、`abilities.jump`、`abilities.move`、`abilities.attackMobs`、`abilities.attackPlayers`、`abilities.build`、`abilities.mine`、`abilities.teleport`。

`query.*`、Molang 表达式、事件快照、NBT、组件、玩家经验等没有对应安全写接口，属于只读状态。
### Client status expansion

The client side exposes position, foot position, velocity/input vector, rotation, effects, item slots, movement flags, camera values, FPS/screen values, view settings, and operation flags through `client.*`.
