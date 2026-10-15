# 对话练习册

从“旭哥带你狙女神”（B站 UID `91690248`）的逐帧约会视频建立来源目录，按集梳理交流题目、现场问答与博主讲解，并标记分类和原视频时间链接。

教程现按“整理集数 → 集内时间 → 交流题目”组织，先系统梳理能辨认的现场问答，再标注分类与视频跳转。集数按照发布时间编排，不代表原作者的官方集数。每条交流记录分开列出现场台词和博主讲解，逐句保留时间点及可追溯的转写片段 ID。

<!-- dialogue-progress:start -->
当前按集梳理：**18 / 18 集、682 条交流记录、18 份完整机器稿**。**实际逐句回听 0 条**。机器文字整理不等于听校；单边台词或混合说话者的记录仍是待核交流单元。
<!-- dialogue-progress:end -->

**当前工具不能直接听取音频，因此实际逐句回听仍未完成。** 本轮复用原音轨，为全部 18 集增加 SenseVoice 独立识别，与原 Whisper、已有其他 Whisper 版本及实际看图核对过的字幕作文字交叉比较。对有来源依据的词形另存阅读修订，不覆盖原始机器稿。仍有歧义的数字、否定、姓名、角色和句界继续待核；两模型相同也不能证明原声准确。

<!-- quality-progress:start -->
2026-10-15 交叉比较：**18 集独立 SenseVoice 稿、680 / 682 条交流记录有交叉来源、697 个文字单元有来源支持的阅读修订**，另有 13 个语义候选待核。已生成 **570 道对应练习**，其中 150 道的题干与对应回应具备交叉依据，默认优先显示；其余仍可按待核题筛选。
<!-- quality-progress:end -->

题目索引见 [DIALOGUES.md](DIALOGUES.md)，原始结构见 `data/dialogue-rounds/`；完整机器稿见 `data/transcripts/`，独立交叉稿见 `data/alternate-transcripts/`。逐轮题目在“对话练习”中；此前 18 条有限摘要与 8 道原创示范题通过“旧版示范”筛选查看。

## 交叉纠错与对应练习

- `data/crosschecks.json` 保存 2,868 个现场台词及讲解文字单元的自动对照、独立来源 ID、差异候选和时间。
- 比较时以 OpenCC 统一繁简、去除标点；繁简和标点变化不计为纠错。按时间邻域做字符对齐，只用于找到差异，不自动替换词句。
- SenseVoice 重叠窗口分别比对；同一模型的多个窗口不算多票。另一个模型有实质不同读法时，不能因某一稿相同而隐藏冲突。
- `data/corrections/` 保存审读后的词形修订：原字、阅读稿、依据、来源片段及整句是否适合练习。修好一个词不代表整段清楚；剩余乱码、关键否定或数字不确定的句子不因此升级。
- 交流记录可以展开“原稿与依据”，并点“练这题”。练习按来源分类、集数和时间组织，先写自己的答案，再展开视频回应、博主讲解和独立点评。原视频回应只是对照材料，没有自动设为唯一正确答案。
- 默认仅显示题干与对应回应具备交叉依据的题目；切换“全部 · 含待核题”可见完整题库。仅有单边台词或无法找到双方角色的记录保留在时间线，不编造问答。
- 518 道回应题、52 道发问题，共 570 道。发问题的提示是学习改写，有明确标注；不是冒充视频原话。全部题库可导出为 JSON，草稿仅存在当前浏览器。

方法与完整音轨处理记录见 [模型研究](research/crosscheck-model-research.md)，修订审读见 [前 9 集](research/crosscheck-review-early.md)、[后 9 集](research/crosscheck-review-late.md)，独立分层抽审及已处理的问题见 [抽审记录](research/crosscheck-correction-audit.md)。这些属于文字来源核验，不能代替实际听校。

## 当前核查结果

核查日期：2026-10-14，时间统一为中国标准时间。

- 12 条标题使用“把妹约会逐帧解析”。
- 6 条使用“把妹约会技巧逐帧解析”或“约会技巧逐帧解析”。
- 合计 18 条，时长 7 小时 43 分 43 秒；逐条验证作者、当前标题、BV 号、CID、发布时间、时长。
- 覆盖公开可见的 12 个合集、110 个不同视频；主合集《实战约会》覆盖 41/41 条。
- 作者全部投稿接口受平台风控限制，不能保证合集外的历史系列视频全部收录。
- 18/18 条匿名播放器字幕查询成功，但字幕列表为空，`need_login_subtitle=true`。这只证明匿名渠道没有返回字幕，不证明登录后也没有字幕。

目录见 [CATALOG.md](CATALOG.md)；完整研究依据见 [research/catalog-research.md](research/catalog-research.md)、[research/catalog-candidates.json](research/catalog-candidates.json)、[research/subtitle-availability.json](research/subtitle-availability.json)。

部分合集里的旧标题与独立视频页当前标题不同，分类以逐条 `view` 查询的当前标题为准。实录与讲解版的配对依据是标题匹配，未做音频逐段对齐。

## 打开网页

静态网页位于 `docs/`，无第三方脚本、外部字体、依赖安装和后端。可以直接用浏览器打开 `docs/index.html`，也可以在本目录执行：

```sh
python3 -m http.server 60435 --bind 127.0.0.1 --directory docs
```

然后访问 `http://127.0.0.1:60435/`。

网页支持标题/BV 号搜索、系列筛选、排序、收藏、目录和题库导出、先答后看解析的逐轮练习，以及按视频管理本机字幕笔记。练习草稿、收藏、说话者标签与笔记存在当前浏览器的 localStorage，清理浏览器数据会删除这些本机记录，请导出重要笔记。

## 逐轮记录与听校

素材提供方已于 2026-10-14 确认自有作品或已获整理、公开发布授权。本仓库因此保存授权范围内的完整机器转写文字与逐轮问答；原媒体不发布。来源标题和原作者信息照实注明。

本次整理遵循这些规则：

1. 阅读每集完整机器稿，按集内时间提取能够辨认的交流单元，短片与长片均不限制为一个情境；不为凑数量编造缺失问答。
2. 现场提问、实际回应、博主讲解分别记录。只有讲解者复述的问题仍归讲解，不伪装成现场原声；角色混合的字幕保留“待标注”。
3. 每句关联真实 source segment IDs，文字与时间边界由构建程序校验；可合并原片段、加标点，不悄悄改换字词。
4. 机器错字保留在来源稿；网站的 `display_text` 可采用有依据的阅读修订，`text` 与原始引用保留不变。修订另存原字、理由与证据，不能称人工或模型回听校对。字幕 OCR 与实际画面文字核对也留独立源 ID，不覆盖原机器稿；字幕采样区间不是精确口语起止。
5. 尚未识别出的答句、讲解回放、画面动作与人物身份分别标记，不能将剪辑中的短回应推定为完整同意。
6. 每条标记分类、整理集数、时间范围、逐句跳转链接和核查状态。网站按发布时间与集内时间排序，支持分类、集数、全文搜索与 JSON 导出。
7. 完整来源机器稿可在“逐句笔记”载入，逐句标注说话者、解析笔记。所有本机改动保持在浏览器中，重新载入保留匹配句的已有笔记，可撤回。

机器识别与语义整理只能覆盖机器稿能辨认的内容，不能保证原音频中的所有交流都已恢复。**实际逐句回听仍未完成**；这项任务的听校验收要求尚未满足。已识别出的拒绝或犹豫照实保留，不因博主后续解释而改写成同意。

### 可导入的 JSON

以下只是格式示意，不是视频原话：

```json
{
  "video_bvid": "BV1f8Yj6aExQ",
  "notes": "这集的概述与独立解析",
  "segments": [
    {"start": 1.2, "end": 3.4, "text": "用户提供并听校的句子", "speaker": "other", "note": "当时的情境"},
    {"start": 3.4, "end": 5.8, "text": "用户提供并听校的回应", "speaker": "responder", "note": "回应起了什么作用"},
    {"start": 5.8, "end": 9.0, "text": "用户提供并听校的讲解", "speaker": "commentary", "note": "博主解释与自己的判断分开"}
  ]
}
```

同时支持 B站字幕 JSON 的 `body` / `from` / `to` / `content` 字段。文件最多 5 MiB、10,000 句。导入时检查 BV 号及时间是否超出当前视频时长；替换字幕时保留匹配句的已有标注，且可撤回上次导入。不会把文件上传到服务器。

## GitHub Pages 发布

公开仓库：[Kirrito-k423/dating-dialogue-tutorial](https://github.com/Kirrito-k423/dating-dialogue-tutorial)。

网页发布到：[对话练习册](https://kirrito-k423.github.io/dating-dialogue-tutorial/)。逐轮题可直接用 `#exercise=drill-BV…-q001` 跳转，原交流记录用 `#round=BV…-q001` 跳转。

原视频按发布者信息注明来源；有限摘要、独立解析和原创建议回应分别标注。

将本目录作为目标仓库的根目录，发布源选择已有分支的 `/docs` 文件夹即可。具体设置：仓库 `Settings → Pages → Build and deployment → Deploy from a branch → 分支 → /docs`。这条路径来自 [GitHub 官方文档](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。

浏览器里的本机笔记没有打包进网页源码，也不会随站点发布。公开内容明确标记机器转写、字幕核对和实际回听状态；后续校订应保留来源依据。

## 维护与验证

```sh
python3 scripts/build.py
python3 -m unittest discover -s scripts -p 'test_course_quality.py'
node --test scripts/subtitles.test.cjs
node --check docs/app.js
```

重新计算跨稿对照需独立 Python 环境（构建和浏览网站本身不依赖 OpenCC）：

```sh
python3 -m venv .venv-crosscheck
.venv-crosscheck/bin/pip install -r scripts/requirements-crosscheck.txt
.venv-crosscheck/bin/python -m unittest discover -s scripts -p 'test_crosscheck_alignment.py'
.venv-crosscheck/bin/python scripts/crosscheck.py
python3 scripts/build.py
```

`scripts/build.py` 从研究目录、交流单元、来源稿、交叉报告及阅读修订生成 `docs/`、`CATALOG.md` 与 `DIALOGUES.md`。它会拒绝源片段 ID 缺失、原字被改、证据正文伪造、跨视频引用、未说明的远距离证据、时间超范围等记录。增加来源或修订后重新生成；不要直接手改生成数据。`verify_ui.cjs` 与 `verify_practice.cjs` 提供真实浏览器的导航、时间链接、作答、隐藏答案、草稿、导出和手机布局检查。

原媒体留在公开仓库之外，保留来源索引与处理统计。原 Whisper small-q5_1 稿和本轮完整 SenseVoice 稿均在本机处理；本轮复用已有音轨，没有再次下载原媒体。没有采集登录 Cookie；未绕过付费或登录校验。公开仓库保存已获授权的完整机器文字稿与逐轮整理；本机保留紧凑音轨、字幕帧证据及可复用模型环境。转换用的临时整轨 WAV 已清理。
