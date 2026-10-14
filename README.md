# 对话练习册

从“旭哥带你狙女神”（B站 UID `91690248`）的逐帧约会视频建立来源目录，最终按“情境 → 对方的问题 → 实际回应 → 博主讲解 → 独立解析”编成学习教程。

当前完成的是**来源目录、可运行网页和陆续加入的有限音频摘要**。公开音频已经可获取，正在使用本地机器识别辅助分析；**逐句回听校对 0 集**。网页将“视频场景意译”与 8 道原创练习分开标记。机器摘要不能当成经过听校的逐字稿。

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

网页支持标题/BV 号搜索、系列筛选、排序、收藏、目录导出、先答后看解析的原创练习，以及按视频管理本机字幕笔记。练习草稿、收藏、说话者标签与笔记存在当前浏览器的 localStorage，清理浏览器数据会删除这些本机记录，请导出重要笔记。

## 音频摘要与逐句记录

对于链接中的第三方视频，可制作有限篇幅的对话意译、讲解摘要和原创分析，并保留原视频时间点与链接。完整逐字稿需要用户提供有权使用的音视频或字幕材料；不能直接把一整套第三方节目转写后公开转载。

1. 优先准备典型视频 `BV1f8Yj6aExQ` 的有权使用的音频或字幕，再建立一集的整理样板。
2. SRT/VTT/JSON 字幕可直接导入“逐句笔记”。网页不包含语音识别功能，音频材料仍需先转写并听校。
3. 播放原视频，区分“对方”“回应者”“博主讲解”“旁白”。字幕识别本身不能可靠判断说话者，默认保留为“待标注”。
4. 不清楚的话标注 `[听不清]`，不补造对话；重要语气、停顿和画面上的解释另记。
5. 将相邻的对方提问与实际回应配成一组。遇到长叙述、多人交谈或中途插入讲解时，不强行整理成一问一答。
6. 对每组写明情境、实际回应、博主的解释、自己的判断、适用条件与可能的其他回应。不要把剪辑结果归因于某一句话，更不要从个别片段推断所有人的心理。
7. 导出 JSON 保留证据。公开教程只加入有依据的有限摘要与独立解析；逐字记录与原媒体默认不进入 `docs/`。

每集应保留单独的处理状态：`目录核实 → 音频取得 → 机器初稿 → 语义审阅与有限摘要 → 逐句回听 → 对话/讲解标注 → 可发布逐字材料`。机器草稿的语义审阅不能替代逐句回听。当前进度见 `research/audio-analysis-progress.json`，有限摘要见 `data/video-summaries*.json`，逐句回听仍为 0 集。

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

网页发布到：[对话练习册](https://kirrito-k423.github.io/dating-dialogue-tutorial/)。目前正在部署；初版包含 18 条目录与前 9 条音频摘要，后续摘要完成后继续更新。

课程文件不声明开源许可证；原视频与标题属于原发布者，本文的有限摘要与独立解析另行标注来源。

将本目录作为目标仓库的根目录，发布源选择已有分支的 `/docs` 文件夹即可。具体设置：仓库 `Settings → Pages → Build and deployment → Deploy from a branch → 分支 → /docs`。这条路径来自 [GitHub 官方文档](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。

GitHub Pages 的默认站点可被公开访问，私有仓库本身不等于私有网页。浏览器里的本机笔记没有打包进网页源码，也不会随站点发布。需要发布的真实内容应先经过听校、来源和可使用范围检查。

## 维护与验证

```sh
python3 scripts/build.py
node --test scripts/subtitles.test.cjs
node --check docs/app.js
```

`scripts/build.py` 从研究目录与 `data/exercises.json` 生成 `docs/data.js`、`docs/catalog.json`、`CATALOG.md`。增加来源时先更新研究依据，再重新生成；不要直接手改生成文件。

临时原媒体可放外置盘 `/Volumes/PSSD/Mac-Storage-Archive/ToBeloved/dating-tutorial/`，保留字幕与索引引用。本次为音频分析短暂取得公开音轨，使用隔离目录中的 whisper.cpp / small-q5_1，串行处理并立即移除已处理的音轨与 WAV。没有采集登录 Cookie；未绕过付费或登录校验。转写全文只作分析中间材料，不作为交付件或发布内容。处理完成后清理隔离工具、模型与完整机器稿，保留有限摘要、版本及校验统计。
