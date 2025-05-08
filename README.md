# 《联机大厅服务器模板》配套附加包

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) [![Minecraft China Edition](https://img.shields.io/badge/Minecraft-Netease_Edition-green)](https://mc.163.com)

这是Minecraft（我的世界）中国版端游联机地图《联机大厅服务器模板》的配套附加包的开源仓库。

---

## 目录

- [项目简介](#项目简介)
- [主要功能](#主要功能)
- [快速开始](#快速开始)
  - [安装要求](#安装要求)
  - [安装步骤](#安装步骤)
- [功能详解](#功能详解)
- [贡献指南](#贡献指南)
- [支持我们](#支持我们)
- [许可证](#许可证)
- [常见问题](#常见问题)

---

## 项目简介

这是Minecraft（我的世界）中国版端游联机地图《联机大厅服务器模板》的配套附加包的开源仓库。本项目是一个完全开源、社区驱动的组件，旨在为服务器管理员和地图创作者提供强大的自定义功能。

## 主要功能

✔️ **自定义附魔** - 突破原版限制，实现任意附魔  
✔️ **隐藏物品获取** - 获取原版隐藏和特殊物品  
✔️ **NBT编辑** - 修改你物品的NBT  
✔️ **指令批处理** - 一次性执行大量指令，提高效率      
✔️ **玩家检测** - 自动识别名字带有违禁词的玩家    
✔️ **指令调用ModAPI** - 使用自定义指令来调用网易的[ModAPI](https://mc.163.com/dev/mcmanual/mc-dev/mcdocs/1-ModAPI/%E6%8E%A5%E5%8F%A3/Api%E7%B4%A2%E5%BC%95%E8%A1%A8.html)    

## 快速开始

### 安装要求

- Minecraft 中国版最新版本（您可以下载[官服](https://mc.163.com/)或[4399渠道服](https://news.4399.com/wdshijie/)）
- 联机大厅服务器模板

### 安装步骤

1. 打开 我的世界中国版 端游启动器
2. 进入"组件中心"
3. 搜索“联机大厅服务器模板”并下载
4. 前往联机大厅创建房间

## 功能详解

部分功能提供用户界面，在聊天框输入以下指令并发送，可打开相应GUI，按提示操作即可。

自定义附魔：`python.enchant`

获取隐藏物品：`python.getitem`

修改物品NBT：`python.nbteditor`

指令批处理：`python.cmdbatch`

修改物品注释：`python.changetips`

**详细内容参见 [📖帮助文档](/docs/index.md)**

## 贡献指南

我们欢迎所有形式的贡献！以下是参与方式：

1. **提交Issue** - 报告bug或建议新功能
2. **Pull Request** - 直接贡献代码
3. **文档改进** - 帮助完善文档和教程
4. **社区支持** - 帮助其他用户解决问题

## 支持我们

如果这个项目对您有帮助，请考虑支持我们的开发：

[![捐赠](https://img.shields.io/badge/Donate-Afdian-green.svg)](https://afdian.com/a/eggylan)

您的支持将帮助我们持续改进这个项目！

## 许可证

本项目采用 **GNU General Public License v3.0** 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 常见问题

❓ **Q: 能用在国际版Minecraft吗？**  
A: 目前仅支持中国版。国际版API受限无法移植。

❓ **Q: 如何报告bug或建议新功能？**  
A: 请在Issues页面提交详细报告。
