<h1 align="center">⚠️ 重要说明 ⚠️</h1>
<h3 align="center">本仓库代码因过于久远，含有大量不规范之处，正在考虑重构。</h3>
<p align="center">如有任何问题或建议，欢迎提交 Issue 讨论。</p>

---

<p align="center">
	<img
		src="https://raw.githubusercontent.com/eggylan/GTMBPlugin/main/readmeimg/icon.png"
		width="120px"
		align="center" alt="GTMB Logo"
	/>
	<h1 align="center">GTMBPlugin</h1>
	<p align="center">
		这是Minecraft（我的世界）中国版附加包 GTMBPlugin 的开源仓库。
	</p>
</p>

<p align="center">
	<a href="https://opensource.org/license/mit">
		<img
			src="https://img.shields.io/badge/License-MIT-blue.svg"
			alt="License: MIT"
		/>
	</a>
	<a href="https://mc.163.com">
		<img
			src="https://img.shields.io/badge/Minecraft-Netease_Edition-green"
			alt="Minecraft Netease Edition"
		/>
	</a>
	<a href="https://deepwiki.com/eggylan/GTMBPlugin">
		<img 
			src="https://deepwiki.com/badge.svg" 
			alt="Ask DeepWiki"
			>
	</a>
</p>

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

这是Minecraft（我的世界）中国版附加包 GTMBPlugin 的开源仓库。本项目是一个完全开源、社区驱动的组件，旨在为服务器管理员和地图创作者提供强大的自定义功能。

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
- Minecraft 中国版开发工作台（您可以在[官网](https://mc.163.com/dev/)下载）

### 安装步骤

1. 下载最新版附加包到本地（推荐使用 `git clone https://github.com/eggylan/GTMBPlugin.git`）
2. 用 MCStudio 把行为包 `GTMBplugin_B` 与资源包 `GTMBplugin_R` 导入你的地图/项目
3. 启动世界，在聊天框输入 `/openui enchant` 验证组件是否生效

> GTMBPlugin 是一个可被任意地图与服务器产品集成的组件。
> 例：联机大厅地图《联机大厅服务器模板》就使用了它。

## 功能详解

部分功能提供用户界面，在聊天框输入以下指令并发送，可打开相应GUI，按提示操作即可。

自定义附魔：`/openui enchant`

获取隐藏物品：`/openui getitem`

修改物品NBT：`/openui nbteditor`

指令批处理：`/openui cmdbatch`

修改物品注释：`/openui changetips`

从本地导入自定义结构：`/openui structureimport`

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

本项目采用 **MIT** 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 常见问题

❓ **Q: 能用在国际版Minecraft吗？**  
A: 目前仅支持中国版。国际版API受限无法移植。

❓ **Q: 如何报告bug或建议新功能？**  
A: 请在Issues页面提交详细报告。
