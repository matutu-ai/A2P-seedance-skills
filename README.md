# A2P Seedance Skills

本仓库保存 `lingguo-seedance-master` Skill 及其演示案例。Skill 的默认终点是**可直接用于 Seedance 的提示词交付包**，不默认生成视频成片。

## 工作流程（五关卡，每关停下等用户确认）

0. **资料体检**：读取客户资料，区分事实、目标、限制与假设，最多问 3 个关键问题。
1. **方向与玩法锁定**：从[玩法卡库](lingguo-seedance-master/references/play-cards.md)推荐最多 3 张卡，用户一次选定玩法、风格、规格、声音与参考图范围。
2. **参考图**：先出电商图/产品参考图的生成提示词（有工具且获同意才实际生成），确认后再往下。
3. **视频方案与提示词**：分镜、Seedance 主提示词及必要的分段提示词，并自检。
4. **交付与迭代**：后期调整按[变更控制](lingguo-seedance-master/references/change-control.md)先报影响范围再执行。

用户说“直接做”可走快速通道，把关卡 1–3 合并为一次确认。项目状态记录在 `templates/` 下的 brief 与 decisions，便于换会话或换 AI 接续。

自检脚本：`lingguo-seedance-master/scripts/lint_prompt.py`（时间轴、素材引用、违禁词）。

入口：[lingguo-seedance-master/SKILL.md](lingguo-seedance-master/SKILL.md)。使用时可显式调用 `$lingguo-seedance-master`。

## 案例

- [关卡演示：气泡水](cases/关卡演示-气泡水/演示对话.md)：**新版流程**，从资料体检到迭代的完整模拟对话（推荐先看这个）。
- [两阶段流程验收（旧流程）](cases/两阶段验收-气泡水/04-验收记录.md)：虚构初始资料、待确认创意方案、模拟确认后的提示词包及自检。模拟确认不代表真实客户批准。
- [气泡水广告演示（旧流程，素材与预演仍可参考）](cases/气泡水广告-15秒/案例.md)：概念参考图与 15 秒分镜动态预演。预演由静态图制作，不是 Seedance 成片。

平台能力和素材引用方式会随模型及使用界面变化，实际项目按目标平台当前官方文档核对。未经用户另行要求，本 Skill 不提交生成、剪辑或发布视频。
