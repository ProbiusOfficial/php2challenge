# php2challenge
【自用x】用于GZCTF平台的PHP题目快速生成与部署工具

> 培训遇到*密，全程断网，拼尽全力无法战胜，只能内网搭平台上题。

程序运作过程：
- 按图示填入PHP代码和生成题目的相关信息。
- 点击构建后，程序会先将代码封装为 index.php 替换到对应PHP版本的模板文件中。
- 使用输入的 题目名称 在`./generated_projects`生成题目文件。
- 使用输入的 容器名称 构建docker。
- 在 GZ::CTF 平台中创建题目。
- 在 GZ::CTF 平台中部署题目。

![image](https://github.com/user-attachments/assets/0f2d5321-0092-49f2-bbc9-6668bb11711a)
