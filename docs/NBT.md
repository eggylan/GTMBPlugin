# 网易 Minecraft 基岩版 NBT 编写入门

## 什么是 NBT？

NBT（Named Binary Tag）是 Minecraft 中使用的一种树状数据结构，用于存储游戏中的各种数据。它以二进制格式存储，但我们通常以 JSON 格式表示和编辑。下面我们讨论的“NBT”均指网易Minecraft基岩版通过Python接口获取的NBT数据。

## NBT 基本结构

NBT 数据通常由键值对组成，其中：

- 键（Key）：表示数据的名称（字符串）
- 值（Value）：可以是基本数据类型或复合类型（列表、对象等）

### 外层结构

物品的基本信息存储在最外层：

```
{
  "count": 1,                     // 物品数量
  "newItemName": "minecraft:axe", // 物品ID
  "durability": 32,               // 耐久值
  "customTips": "",               // 物品注释
  "extraId": "",                  // 额外ID
  "newAuxValue": 0,               // 附加值
  "showInHand": "True",           // 是否在手中显示
  "userData": {}                  // 高级NBT数据
}
```

### userData 结构

`userData` 包含物品的高级属性，使用特殊格式存储不同类型的数据：

```
"userData": {
  "属性名称": {
    "__type__": 类型代号,
    "__value__": 值
  }
}
```

## 数据类型与代号

| 类型代号 | 类型名称     | 示例值                                          |
| -------- | ------------ | ----------------------------------------------- |
| 1        | 字节型       | `{"__type__": 1, "__value__": 10}`              |
| 2        | 短整型       | `{"__type__": 2, "__value__": 100}`             |
| 3        | 整型         | `{"__type__": 3, "__value__": 1000}`            |
| 4        | 长整型       | `{"__type__": 4, "__value__": 10000}`           |
| 5        | 单精度浮点型 | `{"__type__": 5, "__value__": 1.14}`            |
| 6        | 双精度浮点型 | `{"__type__": 6, "__value__": 3.14159}`         |
| 7        | 字节数组     | `{"__type__": 7, "__value__": [1, 2, 3]}`       |
| 8        | 字符串       | `{"__type__": 8, "__value__": "Hello"}`         |
| 9        | 列表         | `{"__type__" : 9, "__value__": ...(递归转换)}`  |
| 10       | 复合标签     | `{"__type__" : 10, "__value__": ...(递归转换)}` |
| 11       | 整型数组     | `{"__type__" : 11, "__value__": IntList}`       |

## 常见属性详解

### 1. 物品名称

```
"display": {
  "Name": {
    "__type__": 8,
    "__value__": "物品名称"
  }
}
```

### 2. 附魔属性

附魔存储在 `ench` 数组中，每个附魔是一个对象：

```
"ench": [
  {
    "id": {"__type__": 2, "__value__": 附魔ID},
    "lvl": {"__type__": 2, "__value__": 等级},
    "modEnchant": {"__type__": 8, "__value__": ""}
  }
]
```

示例附魔ID：

- 9: 锋利 (Sharpness)
- 17: 耐久 (Unbreaking)

### 3. 耐久度

```
"durability": 当前耐久值
```

### 4. 修理成本

```
"RepairCost": {
  "__type__": 3,
  "__value__": 修理经验等级
}
```

## 完整示例

### 示例1：锋利200的金斧

```
{
  "count": 1,
  "newItemName": "minecraft:golden_axe",
  "durability": 32,
  "customTips": "",
  "extraId": "",
  "newAuxValue": 0,
  "showInHand": "True",
  "userData": {
    "RepairCost": {"__type__": 3, "__value__": 0},
    "ench": [
      {
        "lvl": {"__type__": 2, "__value__": 10},
        "id": {"__type__": 2, "__value__": 17},
        "modEnchant": {"__type__": 8, "__value__": ""}
      },
      {
        "lvl": {"__type__": 2, "__value__": 200},
        "id": {"__type__": 2, "__value__": 9},
        "modEnchant": {"__type__": 8, "__value__": ""}
      }
    ],
    "display": {
      "Name": {"__type__": 8, "__value__": "Killer"}
    }
  }
}
```

### 示例2：效率V的钻石镐

```
{
  "count": 1,
  "newItemName": "minecraft:diamond_pickaxe",
  "durability": 1561,
  "customTips": "",
  "extraId": "",
  "newAuxValue": 0,
  "showInHand": "True",
  "userData": {
    "RepairCost": {"__type__": 3, "__value__": 5},
    "ench": [
      {
        "lvl": {"__type__": 2, "__value__": 5},
        "id": {"__type__": 2, "__value__": 15},
        "modEnchant": {"__type__": 8, "__value__": ""}
      }
    ],
    "display": {
      "Name": {"__type__": 8, "__value__": "超级镐"}
    }
  }
}
```

## 注意事项

1. 类型必须正确匹配，否则可能导致游戏崩溃或数据无效
2. 不是所有属性都可以随意修改，某些属性有有效范围限制
3. 过高的数值可能导致游戏崩溃或各种无法描述的Bug
4. 修改NBT前建议先备份存档