EVE Online 中文社区站点 · 发布包
================================

入口页面
--------
index.html   首页（战地记录 / 精选 / 合集 / 时间线 / 招募）
shili.html   军团招募信息页

目录结构
--------
index.html
shili.html
latest.js          首页“最新更新”数据
collections.js     首页合集统计数据
assets/            背景图素材
  neweden.webp
  eve-online-bg.webp
logos/             招募页联盟/军团徽标
.nojekyll          GitHub Pages 用，避免 Jekyll 处理静态资源
README.txt         本说明

上传方式
--------
1. 将本文件夹内的全部文件按原目录结构上传到网站根目录。
2. 确保访问 https://你的域名/ 时能打开 index.html。
3. shili.html 与 index.html 使用相对路径互相跳转，请保持同级。
4. 若使用 GitHub Pages、Cloudflare Pages、Netlify 或 Vercel，
   将本目录整体作为发布目录即可。

运行说明
--------
- 页面可直接双击以 file:// 方式预览。
- B 站视频封面、直播间、统计接口等为外部资源，需要联网加载。
- latest.js 与 collections.js 由本地脚本生成；若暂时不更新，
  删除这两个文件页面仍可使用 HTML 中已写入的静态数据。
- EVE Online 名称与相关素材版权归 CCP hf. 所有。
