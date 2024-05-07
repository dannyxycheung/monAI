# monAI
monAI，基于模仿的印象派AI，打造普通人也能训练和使用的文生图。

第一版有2个功能：
1、识图训练：上传图片，告诉代码这是什么，代码保存图片和图片描述。使用了第三方去背景库rembg；
2、生成图片：告诉代码需要画的内容，代码查询已保存的图片和描述，生成图片。使用了第三方中文分词库jieba；
界面截图：
1、识图训练
![image](https://github.com/dannyxycheung/monAI/assets/130076937/a6ce8944-0440-4e35-9f05-3f9a8837742c)
训练物体：上传图片后点击去掉背景的图片
![image](https://github.com/dannyxycheung/monAI/assets/130076937/4b9a7065-e34a-455e-9149-720fb19bf566)
训练背景：上传图片后点击提交原图/背景
![image](https://github.com/dannyxycheung/monAI/assets/130076937/bfa83037-5a2d-4f5e-b416-f7cca97e36ec)
2、生成图片：
![image](https://github.com/dannyxycheung/monAI/assets/130076937/b7ac9971-1317-4bd6-97e4-06fe1ce5999f)
输入要画的内容，点击开始作画
![image](https://github.com/dannyxycheung/monAI/assets/130076937/7154c2e5-dd69-4cd6-bcd0-b159f6ecbd17)

todo：
1、图片分辨率：暂只支持800X600，即背景图片要求大于等于800X600，物体图片小于等于800X600，其他分辨率暂未支持
2、中文语义分析：当前仅支持基于分词的简单判断，暂未支持复杂语义分析
3、文生图：当前仅支持单一背景和单一物体的合成，暂未支持其他的高级图形处理




