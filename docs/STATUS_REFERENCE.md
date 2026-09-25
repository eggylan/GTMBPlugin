# Status API Reference

所有命令都以实体选择器开头：

```mcfunction
/get_status <target> <status>
/set_status <target> <status> <value>
/set_status_score <target> <status> <objective> [score_holder]
```

状态名不区分大小写；点路径按原字段名读取，因此 NBT、ExtraData、物品 `userData` 的键名保留大小写。

## 向量

| 状态 | 可用分量 | 可写 |
|---|---|---|
| `position` / `xyz` | `.x` `.y` `.z` | 是 |
| `foot_position` | `.x` `.y` `.z` | 否 |
| `rotation` / `rotxy` | `.pitch` `.yaw` `.x` `.y` | 是 |
| `velocity` / `motion` | `.x` `.y` `.z` | 是，瞬时运动向量 |
| `quaternion` | 返回四元数 | 否 |

## 属性

以下任一属性均可读取和设置；`max_` 前缀读取/设置最大值：

`health`、`speed`、`damage`、`underwater_speed`、`hunger`、`saturation`、`absorption`、`lava_speed`、`luck`、`follow_range`、`knockback_resistance`、`jump_strength`、`armor`、`attack_knockback`、`attack_speed`、`explosion_knockback_resistance`、`flying_speed`、`sneaking_speed`、`movement_efficiency`、`water_movement_efficiency`、`block_break_speed`、`mining_efficiency`、`submerged_mining_speed`。

属性修饰符：`modifier.<属性名>`。

## 实体、行为与定义

`id`、`name`、`type`、`engine_type_id`、`alive`、`dimension`、`tags`、`tag.<标签>`、`nbt`、`nbt.<字段>`、`extra`、`extra.<键>`、`mod.<键>`、`components`、`entity_event_components`、`properties`、`motions`、`attack_target`、`entity_owner`、`tame_owner`、`rider`、`riders`、`is_riding`、`entity_scale`、`collision_size`、`gravity`、`jump_power`、`step_height`、`on_fire`、`air`、`max_air`、`air_unit_bubble`、`consuming_air`、`type_family`、`death_time`、`fall_distance`、`entity_definitions`、`entity_links`、`leash_holder`、`mark_variant`、`mob_color`、`mob_strength`、`max_mob_strength`、`trade_level`、`variant`、`has_chest`、`has_saddle`、`angry`、`baby`、`eating`、`illager_captain`、`loot_dropped`、`naturally_spawned`、`out_of_control`、`persistent`、`pregnant`、`roaring`、`sheared`、`sitting`、`stunned`、`tamed`、`ai_blocked`、`orb_experience`、`model_name`。

可写实体状态：`name`、`step_height`、`air`、`max_air`、`gravity`、`jump_power`、`entity_scale`、`orb_experience`、`persistent`、`sitting`、`sheared`、`loot_dropped`、`actor_pushable`、`actor_collidable`、`ai_blocked`、`tag.<标签>`、`extra.<键>`、`mod.<键>`。

## 状态效果

```mcfunction
/get_status @s effects
/get_status @s effect.speed
/get_status @s effect.speed.amplifier
/get_status @s effect.speed.duration_f
/get_status @s effect.speed.active
/set_status @s effect.speed "30,1,1"
/set_status @s effect.speed "0"
```

效果值是 `持续秒数,额外等级,显示粒子`。`0` 删除指定效果。`effects.<下标>.<字段>` 可读取效果列表中的原始字典。

## 玩家

`xp`、`xp_percent`、`total_xp`、`level`、`hunger`、`current_exhaustion`、`max_exhaustion`、`health_level`、`starve_level`、`health_tick`、`starve_tick`、`natural_regen`、`natural_starve`、`enchantment_seed`、`abilities`、`abilities.<字段>`、`can_fly`、`isFlying`、`permission`、`game_type`、`sneaking`、`swimming`、`blocking`、`fishing`、`interact_range`、`interact_center_offset`、`respawn_pos`、`nearby_players`、`selected_slot`、`all_enchants`、`fish_hook`。

参数型读取：`destroy_time.<命名空间方块>`、`exhaustion_ratio.<行为枚举整数>`。

可写：`hunger`、`current_exhaustion`、`max_exhaustion`、`health_level`、`starve_level`、`health_tick`、`starve_tick`、`natural_regen`、`natural_starve`、`enchantment_seed`、`jumpable`、`movable`、`can_fly`、`isFlying`、`attack_mobs`、`attack_players`、`build_ability`、`mine_ability`、`open_containers`、`operate_doors`、`operator_commands`、`teleport_ability`、`muted`、`ban_fishing`、`permission`、`game_type`、`interact_range`、`pickup_area`、`attack_speed_amplifier`。

## 玩家物品

```mcfunction
/get_status @s item.carried
/get_status @s item.carried.userData
/get_status @s item.carried.durability
/get_status @s item.inventory.0
/get_status @s item.armor.3.max_durability
/set_status @s item.carried.durability "200"
/set_status @s item.inventory.0.count "32"
```

- `item.carried`、`item.mainhand`、`held_item`：主手。
- `item.offhand`：副手。
- `item.inventory.<0-35>`：背包槽。
- `item.armor.<0-3>`：盔甲槽。
- 末尾可跟随物品字典任意字段；`durability`、`max_durability` 有专用写接口。
- 直接设置 `item.<位置>` 或 `item.<位置>.<槽位>` 时传 JSON 物品字典；传 `null` 清空。

## 世界

`world.time`、`world.raining`、`world.thunder`、`world.game_type`、`world.difficulty`、`world.difficulty_locked`、`world.game_rules`、`world.game_rules_locked`、`world.game_type_locked`、`world.gravity`、`world.seed`、`world.spawn_position`、`world.spawn_dimension`、`world.piston_max_interaction_count`、`world.disable_command_minecart`、`world.scoreboard_objects`。

## `set_status` 模式与数学表达式

`/set_status <target> <status> <value>` 写入手动值；`/set_status_score <target> <status> <objective> [score_holder]` 先读取 ModSDK 3.9 的实体计分项整数值再写入状态，省略 `score_holder` 时使用每个目标自身。表达式支持 `sqrt` 等数学函数、四则运算、位运算、比较、逻辑运算，并支持 `velocity.x`、`rotation.yaw` 这种状态路径分量。

`<value>` 是字符串参数：**数字与布尔值必须加英文双引号**（如 `/set_status @s hunger "6"`、`/set_status @s isFlying "1"`、`/set_status @s position "100,64,-20"`）。引擎按参数类型校验 token，不加引号的数字会被当作数字类型而报「语法错误」。`/set_status_score` 从计分板取整数，不受该规则影响。

`extern.forward`、`extern.backward`、`extern.leftward`、`extern.rightward`、`extern.rising`、`extern.falling`、`extern.downing`、`extern.climbing` 是本插件提供的只读派生状态；`extern` 返回全部派生值。

## 客户端

`client.query.*`、`client.effects`、`client.effect.<效果名>.<字段>`、`client.dimension`、`client.body_rot`、`client.on_ground`、`client.in_lava`、`client.event.<事件名>.<字段>`、`client.all`。

## 全量快照与事件

`all` 汇总实体直接状态、所有 AttrType、NBT、ExtraData、效果、组件、物品、运动器和适用的玩家状态。`event.<服务端事件名>[.<字段>]` 与 `client.event.<客户端事件名>[.<字段>]` 返回按需订阅后的最近一次事件快照。
## Client status expansion (3.9)

`client.position`, `client.foot_position`, `client.velocity`, `client.velocity.x`, `client.rotation.yaw`, `client.input_vector`, `client.effects`, `client.effect.<name>.<field>`, `client.item.carried`, `client.item.offhand`, `client.item.inventory.<slot>`, `client.item.armor.<slot>`, `client.is_gliding`, `client.is_sprinting`, `client.is_moving`, `client.is_riding`, `client.is_sneaking`, `client.is_in_water`, `client.is_on_ladder`, `client.is_in_scaffolding`, `client.is_fishing`, `client.hunger`, `client.selected_slot`, `client.all_enchants`, `client.fish_hook`, `client.camera.*`, `client.fps`, `client.screen_size`, `client.screen_view`, and `client.operation.*` are available.
