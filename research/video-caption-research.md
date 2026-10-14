# 原视频画面字幕补缺

核查日期：2026-10-14。原视频仍以 `research/catalog-candidates.json` 的 BV 号、CID 与作者核验记录为准。通过第一方公开 [playurl 接口](https://api.bilibili.com/x/player/playurl)取得可访问的低分辨率 AVC 视频，使用正常 UA / Referer 与直接网络，不读取登录 Cookie。签名 CDN 地址只在内存使用，不进入仓库。视频及帧图只作本地分析，公开材料为文字。

以完整 small 机器稿里大于 5 秒的时间轴空档作为采样线索，0.75 秒采样原视频帧；空档不等于静音、无对话或模型漏识别。使用 macOS AVFoundation 解码与 Vision 中文 OCR。结果保存在 `data/alternate-transcripts/*-caption-gaps.json`；OCR 原字保留，可有错字、标志或非对白文字，不自动当成现场台词。

研究者实际通过图片输入核查选定帧后，另建 `*-caption-reviewed*.json`，保留文字、采样时间、图片散列及独立 source segment ID。没有实际看过的 OCR 结果不能标“字幕核对”；所有字幕核对均不是音频回听。字幕可能经过原视频发布者编辑，不能直接证明逐字口语、角色意愿或现场真实性。

已实际核查的一例：[第1集 07:25](https://www.bilibili.com/video/BV1vj6yBDE5r/?t=445)显示字幕“等会咱俩要看电影吗”，与 medium 机器稿字词有差异，采用独立字幕源保留该差异。更多片段由对应集的整理者逐帧核对，具体记录在 `research/dialogue-extraction-early.md` 与 `research/dialogue-extraction-late.md`。

时间区间是字幕采样位置，不是经听校的精确口语边界。原视频时间跳转用于再次核查；所有实际音频听校计数仍为 0。

发布前已校验 95 个核对字幕来源片段引用的图片散列，均与本机保存的原帧一致。统计见 `research/caption-frame-integrity.json`；散列验证只能确认图片身份，不能替代看图或听音频。字幕补缺结束后清理了 13 份临时低分辨率视频副本，释放约 964 MiB；原音轨、全部提取帧和 OCR 日志保留在本机。清理范围见 `research/video-material-cleanup.json`。
