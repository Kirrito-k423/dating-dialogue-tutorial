# “把妹约会逐帧解析”系列目录核验

核验日期：2026-10-14（Asia/Shanghai）。仅获取公开标题、BVID、发布时间、时长、作者 UID 和合集目录；没有下载媒体，没有读取音频，没有转录对话或博主讲解。

## 已确认的范围

已核验当前可见合集中的 **18 条逐帧解析视频**：标题包含“把妹约会逐帧解析”的 `exact_series` 12 条；“把妹约会技巧逐帧解析”或“约会技巧逐帧解析”的 `related_variant` 6 条。18 条视频的独立 `view` API 均返回作者 UID `91690248`、作者名“旭哥带你狙女神”。典型视频为 [BV1f8Yj6aExQ](https://www.bilibili.com/video/BV1f8Yj6aExQ/)，可通过 [第一方视频元数据 API](https://api.bilibili.com/x/web-interface/view?bvid=BV1f8Yj6aExQ) 核验作者和当前标题。

这些视频元数据中的总时长为 **7 小时 43 分 43 秒**。该数字是视频时长相加，不能解释为已经观看或已经分析的时长。各条完整原标题和 API 链接保存在 `catalog-candidates.json`。

**不能宣称已找到作者所有投稿中的全部系列视频。** 当前核验完整覆盖了作者公开合集，但“作者投稿全列表”接口受平台限制，合集之外仍可能存在未收录的视频。

## 完整性证据与限制

1. [作者合集/列表索引](https://api.bilibili.com/x/polymer/web-space/seasons_series_list?mid=91690248&page_num=1&page_size=20) 返回 `items_lists.page={page_num:1,page_size:20,total:13}`，本次取得 12 个合集和 1 个空的“直播回放”列表，已覆盖该索引的全部 13 项，不需要第二页。
2. 12 个合集各使用 `seasons_archives_list` 的第 1 页、每页 100 条；最大合集仅 41 条。每个合集的实际收到数量均等于返回的 `page.total`。12 个合集共取得 110 条不重复的公开视频元数据。各合集的页码、返回总数和实际条数均写入 JSON 的 `collection_coverage`。
3. [主合集《实战约会》](https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid=91690248&season_id=5203303&sort_reverse=false&page_num=1&page_size=100)（ID `5203303`）返回 41/41 条，其中命中逐帧解析标题的 17 条。其余 24 条是实战纪录、预告或其他约会教学，不能因为同处一个合集就计为“逐帧解析”。主合集全部 41 条元数据另存于 JSON 的 `main_collection_members`。
4. [《于小惠实战约会》合集](https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid=91690248&season_id=7899959&sort_reverse=false&page_num=1&page_size=100)（ID `7899959`）返回 1/1 条，补充了一条主合集未收录的标题变体视频 `BV12GQiBrExv`。其他 10 个合集的目录没有命中这三个标题关键词。
5. [作者旧投稿列表接口](https://api.bilibili.com/x/space/arc/search?mid=91690248&pn=1&ps=50) 返回 HTTP 412；`/x/space/wbi/arc/search` 未签名请求返回 `-403 访问权限不足`，正常 WBI 签名请求返回 `-352 风控校验失败`。因此作者全部投稿的分页和总数没有核验成功；未使用登录 Cookie 或绕过校验。
6. 辅助网页检索使用这三个标题词及作者名，命中条目均落在上述目录；搜索结果没有提供可证明完整性的页码或总数，不能用于证明“全量”。

## 标题来源注意事项

典型视频的独立 `view.data.title` 已是“把妹约会逐帧解析”，但该视频响应内的 `ugc_season.sections[].episodes[].arc.title` 仍保留“搭讪约会实战纪录”的旧标题。另有“搭讪176超长腿车模”变为“邂逅176超长腿”等标题修改。分类以候选视频当前独立 `view` 的标题为准；旧内嵌标题保存在 JSON 中，不能据旧合集标题漏掉讲解版。

发布日期统一由第一方 API 的 Unix `pubdate` 按 UTC+08:00 转换。网页搜索缓存可能显示其他时区或旧标题，表中使用当前 API 数据。

## 逐帧解析目录

| 分类 | 发布时间（北京时间） | 时长 | 标题与第一方原视频 |
|---|---|---:|---|
| 标题变体 | 2026-01-31 14:21:14 | 11:25 | [【约会技巧逐帧解析】第一次约会如何破升温关系？实战纪录加讲解！实战约会技巧！约会冷场破解秘籍！](https://www.bilibili.com/video/BV1vj6yBDE5r/) |
| 标题变体 | 2026-02-05 16:31:07 | 11:44 | [【把妹约会技巧逐帧解析】约会遇到女生要礼物破解方法+女生生气如何化解？实战牵手套路！实战纪录加讲解！实战约会技巧！约会冷场破解秘籍！一次约会让女生爱上你！](https://www.bilibili.com/video/BV14gFYzREk4/) |
| 标题变体 | 2026-03-02 14:34:00 | 17:49 | [【把妹约会技巧逐帧解析】约会法拉利女网红！半夜在车里不让我回家！主动请我旅游！普通男生如何吸引高价值女富婆？超强吸引！直接倒追！实战约会技巧！一次约会爱上你！](https://www.bilibili.com/video/BV1kJP5z6EDw/) |
| 标题变体 | 2026-03-23 15:21:41 | 17:28 | [【把妹约会技巧逐帧解析】约会瑜伽美女网红！半路杀出个前男友！被我极限操作反败为胜！普通男生吸引高价值女富婆！超强吸引！直接倒追！实战约会技巧！一次约会爱上你！](https://www.bilibili.com/video/BV1upQdBiEN1/) |
| 标题变体 | 2026-04-03 14:43:46 | 14:14 | [【把妹约会技巧逐帧解析】约会住豪宅女富婆！半夜留我住宿不让我走！废物测试+拉升关系+私密空间操作！普通男生吸引高价值女富婆!实战约会技巧！一次约会爱上你！](https://www.bilibili.com/video/BV1ZX9KBUEip/) |
| 标题变体 | 2026-04-14 14:17:52 | 52:10 | [【把妹约会技巧逐帧解析】头部博主于小惠搭讪当场约会实战纪录！2天内让女生上头痛哭！搭讪快速拉升关系实战讲解！实战约会技巧！快速让女生爱上你！](https://www.bilibili.com/video/BV12GQiBrExv/) |
| 同名系列 | 2026-05-03 13:05:00 | 33:57 | [【把妹约会逐帧解析】邂逅176超长腿【讲解版】当场约会！哥布林打法！全程约会实战技巧讲解！普通男生吸引美女？实战邂逅约会技巧！一次约会爱上你！](https://www.bilibili.com/video/BV1dx9dBnE7d/) |
| 同名系列 | 2026-05-15 13:05:00 | 30:27 | [【把妹约会逐帧解析】搭讪像克拉拉的御姐【讲解版】即时约会牵手喂我吃饭！哥布林打法！全程约会实战技巧操作！普通男生吸引漂亮直播！实战搭讪约会技巧！一次约会爱上你！](https://www.bilibili.com/video/BV14L5Y6GEcG/) |
| 同名系列 | 2026-05-22 13:05:00 | 31:30 | [【把妹约会逐帧解析】邂逅超高冷御姐被拒2次【讲解版】极限反转当场约会！主动约我一起旅游！哥布林打法！全程约会实战技巧操作！搭讪约会技巧！](https://www.bilibili.com/video/BV1sYLi6nEA6/) |
| 同名系列 | 2026-06-03 13:37:37 | 43:11 | [【把妹约会逐帧解析】搭讪175超长腿御姐【讲解版】连续拒绝高难度极限反转！当场约会牵手给我剥虾！哥布林打法！全程约会实战技巧操作！搭讪约会技巧！一次约会爱上你！](https://www.bilibili.com/video/BV1CjV16KEHe/) |
| 同名系列 | 2026-06-14 13:05:00 | 34:28 | [【把妹约会逐帧解析】搭讪180气质熟女老司机【讲解版】当场要我回家做饭！连续拒绝到主动拉我手！哥布林打法！全程约会实战技巧操作！搭讪约会技巧！一次约会爱上你！](https://www.bilibili.com/video/BV1bXJF6iEXn/) |
| 同名系列 | 2026-06-23 13:05:00 | 24:38 | [【把妹约会逐帧解析】搭讪日系可爱甜妹【讲解版】当场连续过肺！女生瞬间脸红！全程害羞！全新哥布林打法！全程约会实战技巧操作！搭讪约会技巧！一次约会爱上你！](https://www.bilibili.com/video/BV1sFj26mEu1/) |
| 同名系列 | 2026-06-30 13:00:15 | 13:04 | [【把妹约会逐帧解析】搭讪175冷艳御姐！当场牵手【讲解版】主动约我去休息！变魔术把妹！全新哥布林打法！全程约会实战技巧操作！搭讪约会技巧！一次约会爱上你！](https://www.bilibili.com/video/BV1tVKf6cE5G/) |
| 同名系列 | 2026-07-07 14:23:06 | 25:22 | [【把妹约会逐帧解析】搭讪175高智御姐【讲解版】变魔术搭讪！全程大尺度对话！当场牵手！全新哥布林打法！全程约会实战技巧操作！搭讪约会技巧！一次约会爱上你！](https://www.bilibili.com/video/BV1VrMt6tEEx/) |
| 同名系列 | 2026-08-06 13:06:43 | 23:23 | [【把妹约会逐帧解析】邂逅百达翡丽女富婆【讲解版】爱她酸臭脚！借充电宝搭讪大尺度对话！当场牵手！哥布林打法！全程约会实战技巧操作！搭讪约会技巧！一次约会爱上你！](https://www.bilibili.com/video/BV1BsuE63EhN/) |
| 同名系列 | 2026-08-21 12:48:23 | 22:49 | [【把妹约会逐帧解析】夜市邂逅平面模特【讲解版】失败边缘起死回生！魔术吸引！大尺度对话！当场牵手！哥布林打法！全程约会实战技巧操作！搭讪约会技巧！一次约会爱上你！](https://www.bilibili.com/video/BV1gb8M6nENB/) |
| 同名系列 | 2026-09-11 12:46:46 | 31:26 | [【把妹约会逐帧解析】邂逅宝马富婆【讲解版】当场送我回家！主动说喜欢渣男！快速拉升关系！当场牵手！哥布林打法！全程约会实战技巧操作！搭讪约会技巧！一次约会爱上你！](https://www.bilibili.com/video/BV1f8Yj6aExQ/) |
| 同名系列 | 2026-09-21 13:17:29 | 24:38 | [【把妹约会逐帧解析】餐厅搭讪开奔驰幼shi【讲解版】全新冷读术！快速拉升关系！当场一起回家！哥布林打法！全程约会实战技巧操作！搭讪约会技巧！一次约会爱上你！](https://www.bilibili.com/video/BV1P5he6SEys/) |

## 合集覆盖记录

| 合集 ID | 名称 | 取得/总数 | 分页 |
|---|---|---:|---|
| 5203303 | [《实战约会》 各种约会套路实景演示](https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid=91690248&season_id=5203303&sort_reverse=false&page_num=1&page_size=100) | 41/41 | 第 1 页，每页 100 条 |
| 5281156 | [《实战聊天》实战把妹记录全流程解析](https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid=91690248&season_id=5281156&sort_reverse=false&page_num=1&page_size=100) | 29/29 | 第 1 页，每页 100 条 |
| 6449087 | [《充电课程》系统学习吸引女生的全套流程](https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid=91690248&season_id=6449087&sort_reverse=false&page_num=1&page_size=100) | 6/6 | 第 1 页，每页 100 条 |
| 9175181 | [线下课纪录片](https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid=91690248&season_id=9175181&sort_reverse=false&page_num=1&page_size=100) | 1/1 | 第 1 页，每页 100 条 |
| 7899959 | [《于小惠实战约会》头部博主实战纪录讲解](https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid=91690248&season_id=7899959&sort_reverse=false&page_num=1&page_size=100) | 1/1 | 第 1 页，每页 100 条 |
| 6901250 | [《认知提升》全方位认知提升不止是把妹](https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid=91690248&season_id=6901250&sort_reverse=false&page_num=1&page_size=100) | 2/2 | 第 1 页，每页 100 条 |
| 7651009 | [《环球把妹攻略》把妹干货纪录片](https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid=91690248&season_id=7651009&sort_reverse=false&page_num=1&page_size=100) | 1/1 | 第 1 页，每页 100 条 |
| 7545191 | [《剧情演绎》真实事件情景还原！](https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid=91690248&season_id=7545191&sort_reverse=false&page_num=1&page_size=100) | 1/1 | 第 1 页，每页 100 条 |
| 5418924 | [《约会Vlog》真实把妹日常杂谈](https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid=91690248&season_id=5418924&sort_reverse=false&page_num=1&page_size=100) | 4/4 | 第 1 页，每页 100 条 |
| 5716535 | [《社会杂谈》社会现象揭露](https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid=91690248&season_id=5716535&sort_reverse=false&page_num=1&page_size=100) | 1/1 | 第 1 页，每页 100 条 |
| 6317820 | [《粉丝问答》评论区经典提问回答](https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid=91690248&season_id=6317820&sort_reverse=false&page_num=1&page_size=100) | 2/2 | 第 1 页，每页 100 条 |
| 5218792 | [《把妹干货》从思维内核彻底提升](https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid=91690248&season_id=5218792&sort_reverse=false&page_num=1&page_size=100) | 21/21 | 第 1 页，每页 100 条 |

## 后续补齐完整目录的条件

若需要把“已核验所有公开合集”提升为“已核验作者所有公开投稿”，需要取得正常可访问的作者投稿列表，按返回的总数覆盖每一页，再对三个标题词及作者 UID 做同样筛选，并核验独立视频元数据。当前记录应在网页明确展示目录覆盖边界。

本研究没有证实标题中的约会情节、作者经验、剪辑真实性或方法效果；标题仅用于目录识别，不能作为互动技巧有效性的证据。
